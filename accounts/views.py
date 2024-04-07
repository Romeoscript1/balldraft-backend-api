from rest_framework.generics import GenericAPIView, RetrieveUpdateAPIView, UpdateAPIView
from .serializers import (
    UserRegisterSerializer, 
    PasswordResetRequestSerializer, 
    SetNewPasswordSerializer,
    LogoutUserSerializer,
    DDConfirmActionAccountSerializer,)

from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication

from .utils import send_code_to_user
from .models import OneTimePassword, User, ReasonToLeave

from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import smart_str, DjangoUnicodeDecodeError
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils import timezone
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist

from django.contrib.auth import get_user_model
from rest_framework.views import APIView
User = get_user_model()

class RegisterUserView(GenericAPIView):
    serializer_class = UserRegisterSerializer

    @transaction.atomic
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            send_code_to_user(user.email)
            return Response({
                'data': serializer.data,
                'message': f'Welcome {user.first_name} to Balldraft. Thanks for signing up. Check your mail for your passcode.'
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

class VerifyUserEmail(GenericAPIView):
    OTP_EXPIRATION_TIME_SECONDS = 90

    def post(self, request):
        otp_code = request.data.get('otp')
        try:
            user_otp_obj = OneTimePassword.objects.get(code=otp_code)
            user = user_otp_obj.user
            if self.is_otp_expired(user_otp_obj):
                user_otp_obj.delete()
                return self.otp_expired_response()

            if not user.is_verified:
                user.is_verified = True
                user.save()
                return Response({"message": "Account email verified successfully"}, status=status.HTTP_200_OK)
            else:
                return Response({"message": "User is already verified"}, status=status.HTTP_204_NO_CONTENT)

        except OneTimePassword.DoesNotExist:
            return self.otp_expired_response()

    def is_otp_expired(self, otp_obj):
        current_time = timezone.now()
        otp_timestamp = otp_obj.time
        time_difference_seconds = (current_time - otp_timestamp).total_seconds()
        return time_difference_seconds > self.OTP_EXPIRATION_TIME_SECONDS

    def otp_expired_response(self):
        return Response({"message": "OTP has expired. You can request another OTP."}, status=status.HTTP_400_BAD_REQUEST)
    
class ResendCodeView(GenericAPIView):
    OTP_EXPIRATION_TIME_SECONDS = 90

    def post(self, request):
        email = request.data.get('email')

        if not email:
            return Response({"message": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            otp_obj = OneTimePassword.objects.get(user__email=email)
            if self.is_otp_expired(otp_obj):
                otp_obj.delete()  
                send_code_to_user(email)  
                return Response({"message": "New OTP sent successfully"}, status=status.HTTP_200_OK)
            else:
                return Response({"message": "OTP is still valid"}, status=status.HTTP_400_BAD_REQUEST)
        except OneTimePassword.DoesNotExist:
            send_code_to_user(email) 
            return Response({"message": "New OTP sent successfully"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"message": "Failed to send new OTP"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def is_otp_expired(self, otp_obj):
        current_time = timezone.now()
        otp_timestamp = otp_obj.time
        time_difference_seconds = (current_time - otp_timestamp).total_seconds()
        return time_difference_seconds > self.OTP_EXPIRATION_TIME_SECONDS


class CustomTokenObtainPairView(TokenObtainPairView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == status.HTTP_200_OK:
            user = User.objects.filter(email=request.data.get('email')).first()
            if user and not user.is_verified:
                raise AuthenticationFailed('Email is not verified')
        return response

login_view = CustomTokenObtainPairView.as_view()

class PasswordResetRequestView(GenericAPIView):
    serializer_class=PasswordResetRequestSerializer
    def post(self, request):
        serializer=self.serializer_class(data=request.data, context={'request':request})
        serializer.is_valid(raise_exception=True)
        return Response({'message':"An email has been send to you to rest you password"}, status=status.HTTP_200_OK)

class PasswordResetConfirm(GenericAPIView):
    def get(self, request, uidb64, token):
        try:
            user_id = smart_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=user_id)
            if PasswordResetTokenGenerator().check_token(user, token):
                return Response({'message': 'Credentials are valid', 'uidb64': uidb64, 'token': token})
            else:
                return Response({'message': 'Token is invalid or has expired'}, status=status.HTTP_401_UNAUTHORIZED)
        except (TypeError, ValueError, DjangoUnicodeDecodeError, User.DoesNotExist):
            return Response({'message': 'Token is invalid or has expired'}, status=status.HTTP_401_UNAUTHORIZED)

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
                    return Response({'detail': 'User is already active', 'code': 'user_already_active'}, status=status.HTTP_400_BAD_REQUEST)
        except ObjectDoesNotExist:
            return Response({'detail': 'Profile does not exist for this user'}, status=status.HTTP_404_NOT_FOUND)

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
    