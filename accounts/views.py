from rest_framework.generics import GenericAPIView, RetrieveUpdateAPIView, UpdateAPIView
from .serializers import (
    UserRegisterSerializer, 
    PasswordResetRequestSerializer, 
    SetNewPasswordSerializer,
    LogoutUserSerializer,
    DDConfirmActionAccountSerializer, TOTPVerificationSerializer)

from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication

from .utils import send_verification_email
from .models import EmailVerificationTOTP, User, ReasonToLeave

from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import smart_str, DjangoUnicodeDecodeError
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils import timezone
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from drf_yasg.utils import swagger_auto_schema

from django.contrib.sites.shortcuts import get_current_site

from django_otp.plugins.otp_totp.models import TOTPDevice
from django_otp.util import random_hex
import pyotp

from django.contrib.auth import get_user_model
from rest_framework.views import APIView
User = get_user_model()

class RegisterUserView(APIView):
    serializer_class = UserRegisterSerializer

    @swagger_auto_schema(request_body=UserRegisterSerializer)
    @transaction.atomic
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            # Generate and send OTP after user is saved
            self.create_and_send_otp(user)
            return Response({
                'data': serializer.data,
                'message': f'Welcome {user.first_name} to Balldraft. Thanks for signing up. Check your mail for your passcode.'
            }, status=status.HTTP_200_OK)
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def create_and_send_otp(self, user):
        otp_obj, created = EmailVerificationTOTP.objects.get_or_create(user=user)
        if not created:
            # If the OTP already exists, update the secret
            otp_obj.secret = pyotp.random_base32()
            otp_obj.save()
        # Call the utility function to send the OTP email
        send_verification_email(user, otp_obj.secret)

class VerifyUserEmail(APIView):
    @swagger_auto_schema(request_body=TOTPVerificationSerializer)
    def post(self, request):
        serializer = TOTPVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data.get('email')
        otp = serializer.validated_data.get('otp')
        
        try:
            user = User.objects.get(email=email)
            verification_record = EmailVerificationTOTP.objects.get(user=user)
            
            totp = pyotp.TOTP(verification_record.secret)
            
            # Verify OTP
            if totp.verify(otp):
                user.is_active = True
                user.save()
                verification_record.delete()
                return Response({'message': 'Email verified successfully.'}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Invalid OTP.'}, status=status.HTTP_400_BAD_REQUEST)
        except (User.DoesNotExist, EmailVerificationTOTP.DoesNotExist):
            return Response({'error': 'Invalid email or OTP.'}, status=status.HTTP_400_BAD_REQUEST)
    
class ResendCodeView(APIView):
    def post(self, request):
        email = request.data.get('email')

        if not email:
            return Response({"message": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
            try:
                otp_obj = EmailVerificationTOTP.objects.get(user=user)
                # If OTP already exists, update the secret
                otp_obj.secret = pyotp.random_base32()
                otp_obj.save()
                # Send new OTP code
                send_verification_email(user, otp_obj.secret)
                return Response({"message": "New OTP sent successfully"}, status=status.HTTP_200_OK)
            except EmailVerificationTOTP.DoesNotExist:
                # Create a new TOTP secret and send the code
                secret = pyotp.random_base32()
                EmailVerificationTOTP.objects.create(user=user, secret=secret)
                send_verification_email(user, secret)
                return Response({"message": "New OTP sent successfully"}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "User with this email does not exist"}, status=status.HTTP_400_BAD_REQUEST)


class CustomTokenObtainPairView(TokenObtainPairView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        # Perform standard token generation
        response = super().post(request, *args, **kwargs)
        
        if response.status_code == status.HTTP_200_OK:
            user = User.objects.filter(email=request.data.get('email')).first()
            if user and TOTPDevice.objects.filter(user=user, name="default").exists():
                # Check if the 2FA token is provided
                if '2fa_token' not in request.data:
                    return Response({
                        'detail': '2FA token required',
                        'access': response.data['access']
                    }, status=status.HTTP_401_UNAUTHORIZED)

                device = TOTPDevice.objects.get(user=user, name="default")
                if not device.verify_token(request.data['2fa_token']):
                    return Response({'error': 'Invalid 2FA token'}, status=status.HTTP_400_BAD_REQUEST)

        return response

login_view = CustomTokenObtainPairView.as_view()

class PasswordResetRequestView(GenericAPIView):
    serializer_class=PasswordResetRequestSerializer
    @swagger_auto_schema(request_body=PasswordResetRequestSerializer)
    def post(self, request):
        serializer=self.serializer_class(data=request.data, context={'request':request})
        serializer.is_valid(raise_exception=True)
        return Response({'message':"An email has been send to you to reset you password"}, status=status.HTTP_200_OK)

class PasswordResetConfirm(GenericAPIView):
    serializer_class=PasswordResetRequestSerializer
    def get(self, request, uidb64, token):
        try:
            user_id = smart_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=user_id)
            if PasswordResetTokenGenerator().check_token(user, token):
                # Generate URL for password reset form
                site_domain = get_current_site(request).domain
                reset_page_url = f"https://{site_domain}/api/v1/auth/set-new-password/{uidb64}/{token}/"
                return Response({'message': 'Token is valid', 'reset_page_url': reset_page_url})
            else:
                return Response({'error': 'Token is invalid or has expired'}, status=status.HTTP_401_UNAUTHORIZED)
        except (TypeError, ValueError, DjangoUnicodeDecodeError, User.DoesNotExist):
            return Response({'error': 'Token is invalid or has expired'}, status=status.HTTP_401_UNAUTHORIZED)
            
class SetNewPassword(GenericAPIView):
    serializer_class = SetNewPasswordSerializer

    def patch(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "Password changed successfully"})

class LogoutUserView(GenericAPIView):
    serializer_class = LogoutUserSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "Logout successful"}, status=status.HTTP_200_OK)

class DeactivateAccountView(APIView):
    serializer_class = DDConfirmActionAccountSerializer
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(request_body=DDConfirmActionAccountSerializer)
    def post(self, request):
        serializer = DDConfirmActionAccountSerializer(data=request.data)
        if serializer.is_valid():
            reason = serializer.validated_data['reason']
            comment = serializer.validated_data['comment']
            
            reason_to_leave = ReasonToLeave.objects.create(
                user=request.user,
                reason=reason,
                comment=comment,
                is_deactivate=True
            )

            user = request.user 
            user.is_deactivate = True
            user.save()
            return Response({'message': 'Account deactivated successfully'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ActivateAccountView(APIView):
    def post(self, request):
        user = request.user
        try:
            with transaction.atomic():
                # profile = Profile.objects.get(user=user)
                reason = ReasonToLeave.objects.get(user=user)
                if user.is_deactivate:  # Check if the user is inactive
                    user.is_deactivate = False
                    reason.delete()
                    user.save()
                    # profile.save()
                    reason.save()
                    return Response({'message': 'Account activated successfully'}, status=status.HTTP_200_OK)
                else:
                    return Response({'error': 'User is already active', 'code': 'user_already_active'}, status=status.HTTP_400_BAD_REQUEST)
        except ObjectDoesNotExist:
            return Response({'error': 'Profile does not exist for this user'}, status=status.HTTP_404_NOT_FOUND)

class DeleteAccountView(APIView):
    def post(self, request):
        serializer = DDConfirmActionAccountSerializer(data=request.data)
        if serializer.is_valid():
            reason = serializer.validated_data['reason']
            comment = serializer.validated_data['comment']
            
            reason_to_leave = ReasonToLeave.objects.create(
                user=request.user,
                reason=reason,
                comment=comment,
                is_delete=True
            )

            user = request.user 
            user.delete()
            return Response({'message': 'Account deleted successfully'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class Enable2FAView(APIView):
    def post(self, request):
        user = request.user
        device, created = TOTPDevice.objects.get_or_create(user=user, name="default")
        if not created:
            return Response({'error': '2FA is already enabled'}, status=status.HTTP_400_BAD_REQUEST)
        
        otp_secret = device.key
        qr_code_url = device.config_url
        return Response({'otp_secret': otp_secret, 'qr_code_url': qr_code_url}, status=status.HTTP_200_OK)
    
class Verify2FATokenView(APIView):
    def post(self, request):
        user = request.user
        token = request.data.get('token')
        try:
            device = TOTPDevice.objects.get(user=user, name="default")
            if device.verify_token(token):
                return Response({'message': '2FA token is valid'}, status=status.HTTP_200_OK)
            return Response({'error': 'Invalid 2FA token'}, status=status.HTTP_400_BAD_REQUEST)
        except TOTPDevice.DoesNotExist:
            return Response({'error': '2FA not set up'}, status=status.HTTP_400_BAD_REQUEST)
        
class Disable2FAView(APIView):
    def post(self, request):
        user = request.user
        try:
            device = TOTPDevice.objects.get(user=user, name="default")
            device.delete()
            return Response({'message': '2FA has been disabled'}, status=status.HTTP_200_OK)
        except TOTPDevice.DoesNotExist:
            return Response({'error': '2FA not set up'}, status=status.HTTP_400_BAD_REQUEST)