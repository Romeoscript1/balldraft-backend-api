import os
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.deconstruct import deconstructible

from accounts.models import User
# from contests.models import Contest

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
    # email = models.CharField(max_length=101, unique=True, blank=True, null=True, verbose_name=_("User Name"))
    # dob = models.DateField(null=True, blank=True)
    address = models.TextField(blank=True, null=True)
    mobile_number = models.CharField(max_length=15, blank=True, null=True)
    bank = models.CharField(max_length=100, null=True, blank=True)
    account_number = models.CharField(max_length=100, null=True, blank=True)
    account_name = models.CharField(max_length=100, null=True, blank=True)
    account_balance = models.FloatField(default=0.00)
    pending_balance = models.FloatField(default=0.00)
    
    image = models.FileField(upload_to=user_profile_image_path, blank=True, null=True)

    @property
    def full_name(self):
        return f"{self.user.first_name} {self.user.last_name}"
    
    @property
    def dob(self):
        return f"{self.user.dob}"
    
    @property
    def email(self):
        return f"{self.user.email}"

    def __str__(self):
        return self.username + "'s Profile"

    
class Bonus(models.Model):
    profile = models.ForeignKey(Profile,on_delete=models.CASCADE)
    username = models.CharField(null=True,blank=True,max_length=200)
    ngn_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    reason = models.TextField(blank=True,null=True)
    seen = models.BooleanField(default=False)
    user_see = models.BooleanField(default=True)
    time = models.DateTimeField(auto_now_add=True,null=True,blank=True)
    verified = models.BooleanField(default=True)
    
    def __str__(self):
        return f'Bonus Sent to {self.username}'
    
    def save(self, *args, **kwargs):
        if self.verified:
            body = f"""
            Dear {self.username},
            {self.reason}
            Note: You can deposit, withdraw, enter contest, and transfer funds in and out of your balldraft account without any transaction fees.
            For any issues with our services, please contact balldraft@balldraft.com"""
            send_email(f"${self.ngn_amount} Free Bonus  | balldraft LTD", body,  self.profile.user.email)
            
            ## credit to their account 
            self.profile.account_balance += self.ngn_amount
            self.profile.account_balance += self.ngn_amount
            self.profile.save()
            
        super().save(*args, **kwargs)
    
class Penalty(models.Model):
    profile = models.ForeignKey(Profile,on_delete=models.CASCADE)
    username = models.CharField(null=True,blank=True,max_length=200)
    ngn_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    reason = models.TextField(blank=True,null=True)
    seen = models.BooleanField(default=False)
    user_see = models.BooleanField(default=True)
    time = models.DateTimeField(auto_now_add=True,null=True,blank=True)
    verified = models.BooleanField(default=True)
    
    def __str__(self):
        return f'{self.profile.username} has been givn a penalty of {self.ngn_amount}'
    
    def save(self, *args, **kwargs):
        if self.verified:
            body = f"""
            Dear {self.username},
            {self.reason}
            
            . For further complains or enquiry, kindly contact balldraft@balldraft.com"""
            send_email(f"${self.ngn_amount}  Penalty Withdrawn from your account  | balldraft LTD", body,  self.profile.user.email)
            
            ## minus to their account
            self.profile.available_balance -= self.ngn_amount
            self.profile.save()
        
        super().save(*args, **kwargs)
  
  
class Notification(models.Model):
    profile = models.ForeignKey(Profile,on_delete=models.CASCADE)
    action = models.TextField(blank=True,null=True)
    time = models.DateTimeField(auto_now_add=True)
    action_title = models.CharField(max_length=100,blank=True,null=True)
    read = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.profile.username} - {self.action}'



class Deposit(models.Model):
    profile = models.ForeignKey(Profile,on_delete=models.CASCADE)
    time = models.DateTimeField(auto_now_add=True)
    amount = models.DecimalField(max_digits=20,decimal_places=5,blank=True,null=True)
    bank_name  = models.CharField(max_length=50,blank=True,null=True)
    account_number = models.CharField(max_length=100,blank=True,null=True)
    ngn_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    verified = models.BooleanField(default=False)
    objects = models.Manager()

    def __str__(self):
        return f'{self.profile.user.username} has deposited this {self.amount}-{self.verified}'

    from django.db.models import Sum
    @classmethod
    def total_amount(cls):
        return cls.objects.aggregate(models.Sum('ngn_amount'))['ngn_amount__sum'] or 0

    @classmethod
    def total_verified_amount(cls):
        return cls.objects.filter(verified=True).aggregate(Sum('ngn_amount'))['ngn_amount__sum'] or 0

    @classmethod
    def total_unverified_amount(cls):
        return cls.objects.filter(verified=False).aggregate(Sum('ngn_amount'))['ngn_amount__sum'] or 0

    def save(self, *args, **kwargs):
        return super().save(*args, **kwargs)



class Withdraw(models.Model):
    profile = models.ForeignKey(Profile,on_delete=models.CASCADE)
    time = models.DateTimeField(auto_now_add=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    bank_name  = models.CharField(max_length=50,blank=True,null=True)
    account_number = models.CharField(max_length=100,blank=True,null=True)
    ngn_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    verified = models.BooleanField(default=False)
    comment =  models.CharField(max_length=100,blank=True,null=True)
    objects = models.Manager()

    def __str__(self):
        return f'{self.profile.user.username} has withdrawn this {self.amount}-{self.verified}'

    @classmethod
    def total_amount(cls):
        return cls.objects.aggregate(models.Sum('ngn_amount'))['ngn_amount__sum']
    @classmethod
    def total_verified_amount(cls):
        return cls.objects.filter(verified=True).aggregate(Sum('amount'))['amount__sum'] or 0

    @classmethod
    def total_unverified_amount(cls):
        return cls.objects.filter(verified=False).aggregate(Sum('amount'))['amount__sum'] or 0


    def save(self, *args, **kwargs):
        return super().save(*args, **kwargs)



class TransactionHistory(models.Model):
    profile = models.ForeignKey(Profile,on_delete=models.CASCADE)
    action = models.TextField(blank=True,null=True)
    time = models.DateTimeField(auto_now_add=True)
    action_title = models.CharField(max_length=100,blank=True,null=True)
    category = models.CharField(max_length=50,blank=True,null=True)

    def __str__(self):
        return f'{self.profile.username} - {self.action}'
