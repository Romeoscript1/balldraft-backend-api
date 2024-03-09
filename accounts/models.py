from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils.translation import gettext_lazy as _ 
from .managers import UserManager
from rest_framework_simplejwt.tokens import RefreshToken
import uuid


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
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)
    auth_provider = models.CharField(max_length=50, default=AUTH_PROVIDERS.get('email'))
    user_name = models.CharField(max_length=101, unique=True, blank=True, null=True, verbose_name=_("User Name"))

    USERNAME_FIELD='email'
    REQUIRED_FIELDS= ["first_name", "last_name", "dob"]

    objects= UserManager()

    def __str__(self):
        return self.email
    
    @property
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def tokens(self):
        refresh=RefreshToken.for_user(self)
        
        return {
            'refresh':str(refresh),
            'access':str(refresh.access_token)
        }
    
    def generate_username(self):
        unique_id = str(uuid.uuid4())[:8]
        username = f"{self.first_name.lower()}.{self.last_name.lower()}.{unique_id}"
        return username

    def save(self, *args, **kwargs):
        if not self.user_name:
            self.user_name = self.generate_username()
        super().save(*args, **kwargs)

class OneTimePassword(models.Model):
    user= models.OneToOneField(User, on_delete=models.CASCADE)
    code=models.CharField(max_length=6, unique=True)
    time = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.user.first_name}-password"

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    address = models.TextField(blank=True, null=True)
    mobile_number = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return self.user.username + "'s Profile"
    
class ReasonToLeave(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    reason = models.CharField(max_length=500)
    comment = models.CharField(max_length=3000, null=True, blank=True)
    is_delete = models.BooleanField(default=False)
    is_deactivate = models.BooleanField(default=False)