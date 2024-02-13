from django.shortcuts import render
from rest_framework.generics import GenericAPIView
from .serializers import (
    UserRegisterSerializer, 
    LoginSerializer, 
    PasswordResetRequestSerializer, 
    SetNewPasswordSerializer,
    LogoutUserSerializer)
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .utils import send_code_to_user
from .models import OneTimePassword, User
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import smart_str, DjangoUnicodeDecodeError
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils import timezone

class RegisterUserView(GenericAPIView):
    serializer_class=UserRegisterSerializer

    def post(self, request):
        user_data=request.data
        serializer=self.serializer_class(data=user_data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            user=serializer.data
            send_code_to_user(user['email'])
            #send email function user['email]

            return Response({
                'data':user,
                'message':f'Welcome {user["first_name"]} to Balldraft. Thanks for signing up. Check your mail for you passcode.'
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

class VerifyUserEmail(GenericAPIView):
    def post(self, request):
        otpcode=request.data.get('otp')
        try:
            user_otpcode_obj=OneTimePassword.objects.get(code=otpcode)
            user = user_otpcode_obj.user

            # checking expiration of otp
            current_time = timezone.now()
            otp_timestamp = user_otpcode_obj.time
            if (current_time - otp_timestamp).total_seconds() > 60:
                user_otpcode_obj.delete()
                return Response({"message": "OTP has expired. You can request another OTP."}, status=status.HTTP_400_BAD_REQUEST)

            if not user.is_verified:
                user.is_verified=True
                user.save()
                return Response(
                    {"message":"Account email verified succesfully"},
                    status=status.HTTP_200_OK
                )
            return Response({
                "message":"otp code is invalid. User already verified"
            }, status=status.HTTP_204_NO_CONTENT)
        except OneTimePassword.DoesNotExist:
            return Response({"message": "OTP has expired. You can request another OTP."}, status=status.HTTP_400_BAD_REQUEST)

class LoginUserView(GenericAPIView):
    serializer_class = LoginSerializer
    
    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={"request":request})
        print(serializer)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class PasswordResetRequestView(GenericAPIView):
    serializer_class=PasswordResetRequestSerializer
    def post(self, request):
        serializer=self.serializer_class(data=request.data, context={'request':request})
        serializer.is_valid(raise_exception=True)
        return Response({'message':"An email has been send to you to rest you password"}, status=status.HTTP_200_OK)

class PasswordResetConfirm(GenericAPIView):
    def get(self, request, uidb64, token):
        try:
            user_id=smart_str(urlsafe_base64_decode(uidb64))
            user=User.objects.get(id=user_id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                return Response({'message': 'token is invalid or has expired'}, status=status.HTTP_401_UNAUTHORIZED)
            return Response({'success':True,'message':'credentials is valid', 'uidb64':uidb64, 'token':token}, status=status.HTTP_200_OK)
            
        except DjangoUnicodeDecodeError:
            return Response({'message': 'token is invalid or has expired'}, status=status.HTTP_401_UNAUTHORIZED)
        
class SetNewPassword(GenericAPIView):
    serializer_class=SetNewPasswordSerializer
    def patch(self, request):
        serializer=self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({"message":'password changed successfully'})

class LogoutUserView(GenericAPIView):
    serializer_class=LogoutUserSerializer
    permission_classes=[IsAuthenticated]

    def post(self, request):
        serializer=self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
# {
#     "email":"test@user.com",
#     "first_name":"test",
#     "last_name":"user",
#     "dob":"2000-02-13",
#     "password":"test123",
#     "password2":"test123"
# }