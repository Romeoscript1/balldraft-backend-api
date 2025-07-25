from datetime import timedelta, datetime
from rest_framework import serializers
from .models import User, EmailVerificationTOTP

from rest_framework.exceptions import AuthenticationFailed

from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_str, DjangoUnicodeDecodeError
from .utils import send_reset_password_email

from rest_framework_simplejwt.tokens import RefreshToken, TokenError, AccessToken

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError

class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=68, min_length=8, write_only=True)
    confirm_password = serializers.CharField(max_length=68, min_length=8, write_only=True)

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'password', 'confirm_password', 'dob']

    def validate(self, attrs):
        password = attrs.get('password')
        confirm_password = attrs.pop('confirm_password', None)
        email = attrs.get('email')
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError({"error": "user with this Email Address already exists."})
        if password != confirm_password:
            raise serializers.ValidationError({"error": "Passwords do not match"})
        try:
            validate_password(password)
        except DjangoValidationError as e:
            raise serializers.ValidationError({'error': e.messages})
        return attrs

    def create(self, validated_data):
        validated_data.pop('confirm_password', None)
        return User.objects.create_user(**validated_data)


class TOTPVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6, min_length=6)

        
class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255, min_length=6)

    def validate(self, attrs):
        email = attrs.get('email')
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            uidb64 = urlsafe_base64_encode(force_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)
            request = self.context.get('request')
            site_domain = get_current_site(request).domain
            relative_link = f"/api/v1/auth/password-reset-confirm/{uidb64}/{token}/"
            abslink = f"http://{site_domain}{relative_link}"
            email_body = f"Hey, Reset your password using this link \n {abslink}"
            data = {
                'email_body': email_body,
                'email_subject': 'Reset your Password',
                'to_email': user.email
            }
            send_reset_password_email(data)
        else:
            raise serializers.ValidationError({"error": "user with this Email Address does not exist."})
        return super().validate(attrs)

class SetNewPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(max_length=68, min_length=8, write_only=True)
    confirm_password = serializers.CharField(max_length=68, min_length=6, write_only=True)
    uidb64 = serializers.CharField(write_only=True)
    token = serializers.CharField(write_only=True)

    def validate(self, attrs):
        password = attrs.get('password')
        confirm_password = attrs.get('confirm_password')
        uidb64 = attrs.get('uidb64')
        token = attrs.get('token')
        
        if password != confirm_password:
            raise serializers.ValidationError({"error":"Passwords do not match"})

        try:
            user_id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=user_id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                raise AuthenticationFailed({"error": "Reset link is invalid or has expired"})
            return attrs
        except (TypeError, ValueError, DjangoUnicodeDecodeError, User.DoesNotExist):
            raise AuthenticationFailed({"error": "Reset link is invalid or has expired"})

    def save(self):
        password = self.validated_data['password']
        user_id = force_str(urlsafe_base64_decode(self.validated_data['uidb64']))
        user = User.objects.get(id=user_id)
        user.set_password(password)
        user.save()
        return user
        
class LogoutUserSerializer(serializers.Serializer):
    refresh_token = serializers.CharField(max_length=255, write_only=True)
    access_token = serializers.CharField(max_length=255, write_only=True)

    def validate(self, attrs):
        refresh_token = attrs.get('refresh_token')
        access_token = attrs.get('access_token')

        if not refresh_token:
            raise serializers.ValidationError({"error": "Refresh token is required"})
        if not access_token:
            raise serializers.ValidationError({"error": "Access token is required"})

        return attrs

    def save(self, **kwargs):
        try:
            refresh_token = self.validated_data['refresh_token']
            access_token = self.validated_data['access_token']

            # Blacklist the refresh token
            token = RefreshToken(refresh_token)
            token.blacklist()

            past_time = datetime.now() - timedelta(days=1)  # Set to expire 1 day ago
            access_token_obj = AccessToken(access_token)
            access_token_obj.set_exp(past_time)
            access_token_obj.save()

        except TokenError as e:
            raise AuthenticationFailed(str(e))
        

class ActivateAccountSerializer(serializers.Serializer):
    confirmation = serializers.BooleanField()

    def validate_confirmation(self, value):
        if not value:
            raise serializers.ValidationError({"error": "Confirmation is required"})
        return value

REASON_CHOICES = [
    ('No reason provided', 'No reason provided'),
    ('Violation of terms', 'Violation of terms'),
    ('Personal reasons', 'Personal reasons'),
]

#deactivate and delete
class DDConfirmActionAccountSerializer(serializers.Serializer):
    reason = serializers.ChoiceField(choices=REASON_CHOICES, required=True)
    comment = serializers.CharField(max_length=3000, required=False)
    password = serializers.CharField(required=True)
    # confirmation = serializers.BooleanField()

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

    def validate_password(self, value):
        if self.request:
            user = self.request.user
            if not user.check_password(value):
                raise serializers.ValidationError({"error": "Incorrect password"})
        return value

# class DeleteAccountSerializer(serializers.Serializer):
#     reason = serializers.CharField(choices=REASON_CHOICES, max_length=500, required=False)
#     comment = serializers.CharField(max_length=3000, required=False)
#     password = serializers.CharField(required=True)
#     # confirmation = serializers.BooleanField()

#     # def validate_confirmation(self, value):
#     #     if not value:
#     #         raise serializers.ValidationError("Confirmation is required")
#     #     return value
    
#     def validate_password(self, value):
#         user = self.context['request'].user
#         if not user.check_password(value):
#             raise serializers.ValidationError("Incorrect password")
#         return value
