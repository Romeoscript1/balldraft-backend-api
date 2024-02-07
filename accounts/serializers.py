from rest_framework import serializers
from .models import User
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed

#for resetting passwrod
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import smart_str, smart_bytes, force_str
from django.urls import reverse
from .utils import send_reset_password_email

from rest_framework_simplejwt.tokens import RefreshToken, TokenError



class UserRegisterSerializer(serializers.ModelSerializer):
    password=serializers.CharField(max_length=68, min_length=8, write_only=True)
    password2=serializers.CharField(max_length=68, min_length=8, write_only=True)

    class Meta:
        model=User
        fields=['email', 'first_name', 'last_name', 'password', 'dob','password2']

    def validate(self, attrs):
        password= attrs.get('password', '')
        password2= attrs.get('password2', '')
        if password != password2:
            raise serializers.ValidationError("passwords do not match")
        return attrs
        # return super().validate(attrs)
    
    def create(self, validated_data):
        user=User.objects.create_user(
            email=validated_data['email'],
            first_name=validated_data.get('first_name'),
            last_name=validated_data.get('last_name'),
            dob=validated_data.get('dob'),
            password=validated_data.get('password')
        )
        return user
        # return super().create(validated_data)
    
class LoginSerializer(serializers.ModelSerializer):
    email=serializers.EmailField(max_length=255, min_length=6)
    password=serializers.CharField(max_length=68, write_only=True)
    full_name=serializers.CharField(max_length=255, write_only=True, required=False)
    access_token=serializers.CharField(max_length=255, write_only=True, required=False)
    refresh_token=serializers.CharField(max_length=255, write_only=True, required=False)

    class Meta:
        model=User
        fields=['email','password',
                'full_name','access_token','refresh_token'
                ]

    def validate(self, attrs):
        email=attrs.get('email')
        password=attrs.get('password')
        request=self.context.get('request')
        user = authenticate(request, email=email, password=password)
        print(user)
        if not user:
            raise AuthenticationFailed('Invalid crendentials try again')
        if not user.is_verified:
            raise AuthenticationFailed("Email is not verified")
        user_tokens=user.tokens()

        response_data = {
            'email': user.email,
            'full_name': user.get_full_name,
            'access_token': user_tokens['access'],
            'refresh_token': user_tokens['refresh']
        }

        return response_data

class PasswordResetRequestSerializer(serializers.Serializer):
    email=serializers.EmailField(max_length=255, min_length=6)

    class Meta:
        fields=['email']

    def validate(self, attr):
        email=attr.get('email')
        if User.objects.filter(email=email).exists():
            user=User.objects.get(email=email)
            uidb64=urlsafe_base64_encode(smart_bytes(user.id))
            token=PasswordResetTokenGenerator().make_token(user)
            request=self.context.get('request')
            site_domain=get_current_site(request).domain
            relative_link=reverse('password_reset_confirm', kwargs={'uidb64':uidb64, 'token':token})
            abslink=f"http://{site_domain}{relative_link}"
            email_body=f"Hey, Reset your password using this link \n {abslink}"

            data={
                'email_body':email_body,
                'email_subject':'Reset your Password',
                'to_email':user.email
            }
            send_reset_password_email(data)
        return super().validate(attr)
    
class SetNewPasswordSerializer(serializers.Serializer):
    password=serializers.CharField(max_length=68, min_length=8, write_only=True)
    confirm_password=serializers.CharField(max_length=68, min_length=6, write_only=True)
    uidb64=serializers.CharField(write_only=True)
    token=serializers.CharField(write_only=True)

    class Meta:
        fields = ['password', "confirm_password", "uidb64", 'token']

    def validate(self, attrs):
        try:
            token=attrs.get('token')
            uidb64=attrs.get('uidb64')
            password=attrs.get('password')
            confirm_password=attrs.get('confirm_password')

            user_id= force_str(urlsafe_base64_decode(uidb64))
            user=User.objects.get(id=user_id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                raise AuthenticationFailed("reset link is invalid or has expired", 401)
            if password != confirm_password:
                raise AuthenticationFailed("password do not match")
            user.set_password(password)
            user.save()
            return user
        
        except Exception:
            raise AuthenticationFailed("reset link is invalid or has expired", 401)
        
class LogoutUserSerializer(serializers.Serializer):
    refresh_token=serializers.CharField(max_length=255, write_only=True, required=False)

    default_error_message={
        'bad_token':('Token is invalid or has expired')
    }

    def validate(self, attrs):
        self.token=attrs.get('refresh_token')
        return attrs
    
    def save(self, **kwargs):
        try:
            token=RefreshToken(self.token)
            token.blacklist()
        except TokenError:
            return self.fail('bad_token')