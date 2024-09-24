import os
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils.translation import gettext_lazy as _ 
from .managers import UserManager
from rest_framework_simplejwt.tokens import RefreshToken

# from contests.models import Contest
import pyotp
from .models import *


AUTH_PROVIDERS={
    'email':'email',
    'google':'google'
}




class User(AbstractBaseUser, PermissionsMixin):
    email=models.EmailField(max_length=255, unique=True, verbose_name=_("Email Address"))
    first_name = models.CharField(max_length=100, verbose_name=_("First Name"))
    last_name = models.CharField(max_length=100, verbose_name=_("Last Name"))
    dob = models.DateField()
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_deactivate = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)
    auth_provider = models.CharField(max_length=50, default=AUTH_PROVIDERS.get('email'))

    USERNAME_FIELD='email'
    REQUIRED_FIELDS= ["first_name", "last_name", "dob"]

    objects= UserManager()

    def __str__(self):
        return self.email
    
    def tokens(self):
        refresh=RefreshToken.for_user(self)
        
        return {
            'refresh':str(refresh),
            'access':str(refresh.access_token)
        }

class EmailVerificationTOTP(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    secret = models.CharField(max_length=16, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - {self.secret}"
    
    def generate_otp(self):
        # Create a TOTP instance with a 90-second interval
        totp = pyotp.TOTP(self.secret, interval=90)
        return totp.now()
    
class ReasonToLeave(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reason = models.CharField(max_length=500)
    comment = models.CharField(max_length=3000, null=True, blank=True)
    is_delete = models.BooleanField(default=False)
    is_deactivate = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Reason to Leave"
        verbose_name_plural = "Reasons to Leave"


class Referral(models.Model):
    user = models.ForeignKey(User, related_name="referrals", on_delete=models.CASCADE)
    username = models.CharField(max_length=50)
    date_joined = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.email} referred {self.username}'

