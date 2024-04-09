import os
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.deconstruct import deconstructible

from accounts.models import User
from contests.models import Contest

@deconstructible
class GenerateProfileImagePath(object):

    def __int__(self):
        pass

    def __call__(self, instance, filename):
        ext = filename.split('.')[-1]
        path = f"media/accounts/{instance.user.id}/images/"
        name = f"profile_image.{ext}"
        return os.path.join(path, name)

user_profile_image_path = GenerateProfileImagePath()

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    username = models.CharField(max_length=101, unique=True, blank=True, null=True, verbose_name=_("User Name"))
    address = models.TextField(blank=True, null=True)
    mobile_number = models.CharField(max_length=15, blank=True, null=True)
    bank = models.CharField(max_length=100, null=True, blank=True)
    account_number = models.CharField(max_length=100, null=True, blank=True)
    account_name = models.CharField(max_length=100, null=True, blank=True)
    account_balance = models.FloatField(default=0.00)
    pending_balance = models.FloatField(default=0.00)
    
    image = models.FileField(upload_to=user_profile_image_path, blank=True, null=True)

    contests = models.ManyToManyField(Contest, through='ContestEntry', related_name='participants', blank=True)

    def __str__(self):
        return self.username + "'s Profile"

class ContestEntry(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    contest = models.ForeignKey(Contest, on_delete=models.CASCADE)
    entry_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('profile', 'contest', 'entry_time')  # Ensure uniqueness of entries

    def __str__(self):
        return f"{self.profile.username} entered {self.contest} at {self.entry_time}"