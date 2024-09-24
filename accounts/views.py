from rest_framework.generics import GenericAPIView, RetrieveUpdateAPIView, UpdateAPIView
from .serializers import (
    UserRegisterSerializer, 
    PasswordResetRequestSerializer, 
    SetNewPasswordSerializer,
    LogoutUserSerializer,
    DDConfirmActionAccountSerializer, OTPSerializer,ReferralSerializer)

from rest_framework_simplejwt.views import TokenObtainPairView
from django.db import IntegrityError
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from django.shortcuts import redirect

from .utils import send_code_to_user, hash_otp, generate_otp
from .models import OneTimePassword, User, ReasonToLeave, Referral

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.urls import reverse

from .models import Referral
from django.core.mail import send_mail

from profiles.models import Profile, Notification
from django.conf import settings
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import smart_str, DjangoUnicodeDecodeError
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils import timezone
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from drf_yasg.utils import swagger_auto_schema

from django.contrib.sites.shortcuts import get_current_site

from django_otp.plugins.otp_totp.models import TOTPDevice

from django.contrib.auth import get_user_model
from rest_framework.views import APIView
User = get_user_model()

from django.conf import settings

OTP_EXPIRATION_TIME_SECONDS = settings.OTP_EXPIRATION_TIME_SECONDS

import logging

logger = logging.getLogger(__name__)



class ReferralListView(generics.ListAPIView):
    serializer_class = ReferralSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Referral.objects.filter(user=self.request.user)
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        referral_link = f"{request.scheme}://{request.get_host()}{reverse('register')}?referral_code={request.user.profile.username}"

        if not queryset.exists():
            return Response({"message": "No referrals", "referral_link": referral_link}, status=200)

        serializer = self.get_serializer(queryset, many=True)
        return Response({"referrals": serializer.data, "referral_link": referral_link})



class RegisterUserView(APIView):
    serializer_class = UserRegisterSerializer

    @transaction.atomic
    def post(self, request):
        referral_code = request.query_params.get('referral_code', None)
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():

            user = serializer.save()  # Create the user

            # Allow time for the profile creation via post_save signal
            try:
                profile = Profile.objects.get(user=user)
            except Profile.DoesNotExist:
                # If for some reason the Profile isn't created, return an error
                return Response(
                    {'error': 'An error occurred while creating your profile. Please try again.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Handle referral logic if a referral code is provided
            if referral_code:
                try:
                    # Check if the referrer profile exists
                    referrer_profile = Profile.objects.get(username=referral_code)
                    print(referrer_profile)
                    if referrer_profile.user == user:
                        return Response(
                            {'error': 'You cannot use your own referral code.'},
                            status=status.HTTP_400_BAD_REQUEST
                        )

                    # Set the referred_by field in the new user's profile
                    profile.referred_by = referrer_profile.username
                    profile.save()

                    # Create the referral record
                    Referral.objects.create(user=referrer_profile.user, username=referrer_profile.username)

                    # Update referrer profile balances and referral count:: Later things
                    referrer_profile.account_balance += 0 
                    referrer_profile.referral_people += 1  
                    referrer_profile.save()

                    # Create a notification for the referrer
                    Notification.objects.create(
                        profile=referrer_profile,
                        action=f"{referrer_profile.username} registered using your referral link.",
                        action_title="New Referral",
                    )

                    # Send email notification to the referrer
                    send_mail(
                        'You have a new referral!',
                        f'{referrer_profile.username} has registered using your referral link. You have earned a bonus.',
                        settings.DEFAULT_FROM_EMAIL,
                        [referrer_profile.user.email],
                        fail_silently=False,
                    )

                except Profile.DoesNotExist:
                    # Handle the case where the referral code is invalid
                    transaction.set_rollback(True)
                    return Response(
                        {'error': 'Invalid referral code. Please make sure you are using a valid referral link.'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            # Generate and send OTP after user is saved
            self.create_and_send_otp(user)
            return Response({
                'data': serializer.data,
                'message': f'Welcome {user.first_name} to the platform. Check your mail for your passcode.'
            }, status=status.HTTP_201_CREATED)

        # Handle the case where the serializer is not valid
        logger.error(f"Serializer errors: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def create_and_send_otp(self, user):
        otp_obj, created = EmailVerificationTOTP.objects.get_or_create(user=user)
        if not created:
            otp_obj.secret = pyotp.random_base32()
        else:
            otp_obj.secret = pyotp.random_base32()
        otp_obj.save()

        send_verification_email(user, otp_obj.secret)



class VerifyUserEmail(GenericAPIView): 
    
    @swagger_auto_schema(request_body=OTPSerializer)
    def post(self, request):
        otp_code = request.data.get('otp')
        email = request.data.get('email')

        if not otp_code or not email:
            return Response({"message": "OTP and email are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            otp_obj = OneTimePassword.objects.get(email=email)

            if otp_obj.is_expired():
                otp_obj.delete()
                return Response({"message": "OTP has expired. You can request another OTP."}, status=status.HTTP_400_BAD_REQUEST)

            hashed_otp_code = hash_otp(otp_code)
            if otp_obj.code == hashed_otp_code:
                user = User.objects.get(email=email)
                if not user.is_verified:
                    user.is_verified = True
                    user.save()
                    return Response({"message": "Account email verified successfully"}, status=status.HTTP_200_OK)
                else:
                    return Response({"message": "User is already verified"}, status=status.HTTP_204_NO_CONTENT)
            else:
                return Response({"message": "Invalid OTP."}, status=status.HTTP_400_BAD_REQUEST)

        except OneTimePassword.DoesNotExist:
            return Response({"message": "Invalid or expired OTP."}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({"message": "User not found."}, status=status.HTTP_400_BAD_REQUEST)
        
class ResendCodeView(APIView):
    def post(self, request):
        email = request.data.get('email')

        if not email:
            return Response({"error": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
            existing_otp = OneTimePassword.objects.filter(email=email).first()
            if existing_otp:
                if existing_otp.is_expired():
                    existing_otp.delete()
                    send_code_to_user(email)  
                    return Response({"message": "New OTP sent successfully"}, status=status.HTTP_200_OK)
                else:
                    return Response({"error": "OTP previously sent is still valid"}, status=status.HTTP_400_BAD_REQUEST)

        except OneTimePassword.DoesNotExist:
            send_code_to_user(email) 
            return Response({"message": "New OTP sent successfully"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": "Failed to send new OTP"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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