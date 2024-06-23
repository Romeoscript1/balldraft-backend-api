import os
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.deconstruct import deconstructible

from accounts.models import User
from django.utils.timezone import now
from django.contrib.auth import get_user_model
from datetime import date
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags


def send_email(subject,body,recipient):
    name = "Balldraft Fantasy"
    address = "Balldraft Fantasy Club"
    phone_number = "support@balldraft.com"
    context ={
        "subject": subject,
        "body":body,
        "name": name,
        "address": address,
        "phone_number":phone_number
        }
    html_content = render_to_string("emails.html", context)
    text_content = strip_tags(html_content)
    email = EmailMultiAlternatives(
        subject,
        text_content,
        settings.EMAIL_HOST_USER ,
        [recipient]
    )
    email.attach_alternative(html_content, 'text/html')
    email.send()


class Notification(models.Model):
    profile = models.ForeignKey(Profile,on_delete=models.CASCADE)
    action = models.TextField(blank=True,null=True)
    time = models.DateTimeField(auto_now_add=True)
    action_title = models.CharField(max_length=100,blank=True,null=True)
    read = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.profile.username} - {self.action}'

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
    email = models.CharField(max_length=101, unique=True, blank=True, null=True, verbose_name=_("User Name"))
    dob = models.DateField(null=True, blank=True)
    address = models.TextField(blank=True, null=True)
    mobile_number = models.CharField(max_length=15, blank=True, null=True)
    bank = models.CharField(max_length=100, null=True, blank=True)
    account_number = models.CharField(max_length=100, null=True, blank=True)
    account_name = models.CharField(max_length=100, null=True, blank=True)
    account_balance = models.FloatField(default=0.00)
    pending_balance = models.FloatField(default=0.00)
    
    image = models.FileField(upload_to=user_profile_image_path, blank=True, null=True)

    def __str__(self):
        return self.username + "'s Profile"


class Bonus(models.Model):
    profile = models.ForeignKey('Profile', on_delete=models.CASCADE)
    username = models.CharField(null=True, blank=True, max_length=200)
    ngn_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    reason = models.TextField(blank=True, null=True)
    seen = models.BooleanField(default=False)
    user_see = models.BooleanField(default=True)
    time = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    verified = models.BooleanField(default=True)
    
    def __str__(self):
        return f'Bonus Sent to {self.username}'
    
    def save(self, *args, **kwargs):
        if self.verified:
            body = f"""
            Dear {self.username},
            {self.reason}
            Note: You can deposit, withdraw, enter contest, and transfer funds in and out of your balldraft account without any transaction fees.
            For any issues with our services, please contact support@balldraft.com"""
            send_email(f"${self.ngn_amount} Free Bonus  | balldraft Fantasy", body, self.profile.user.email)
            
            # Credit to their account
            self.profile.account_balance += self.ngn_amount
            self.profile.save()

            # Create a notification
            Notification.objects.create(
                profile=self.profile,
                action=f"Bonus of {self.ngn_amount} has been credited to your account.",
                action_title="Bonus Credited"
            )
            
        super().save(*args, **kwargs)

class Penalty(models.Model):
    profile = models.ForeignKey('Profile', on_delete=models.CASCADE)
    username = models.CharField(null=True, blank=True, max_length=200)
    ngn_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    reason = models.TextField(blank=True, null=True)
    seen = models.BooleanField(default=False)
    user_see = models.BooleanField(default=True)
    time = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    verified = models.BooleanField(default=True)
    
    def __str__(self):
        return f'{self.profile.username} has been given a penalty of {self.ngn_amount}'
    
    def save(self, *args, **kwargs):
        if self.verified:
            body = f"""
            Dear {self.username},
            {self.reason}
            For further complains or enquiry, kindly contact support@balldraft.com"""
            send_email(f"${self.ngn_amount} Penalty Withdrawn from your account | balldraft Fantasy", body, self.profile.user.email)
            
            # Deduct from their account
            self.profile.available_balance -= self.ngn_amount
            self.profile.save()

            # Create a notification
            Notification.objects.create(
                profile=self.profile,
                action=f"Penalty of {self.ngn_amount} has been deducted from your account.",
                action_title="Penalty Deducted"
            )
        
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
        Notification.objects.create(
                profile=self.profile,
                action=f"Penalty of {self.ngn_amount} has been deposited into your account.",
                action_title=f"{self.ngn_amount} NGN Deposit"
            )
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
        Notification.objects.create(
                profile=self.profile,
                action=f"Penalty of {self.ngn_amount} has been withdrawn into your bank account.",
                action_title=f"{self.ngn_amount} NGN Withdrawal"
            )
        return super().save(*args, **kwargs)



class TransactionHistory(models.Model):
    profile = models.ForeignKey(Profile,on_delete=models.CASCADE)
    action = models.TextField(blank=True,null=True)
    time = models.DateTimeField(auto_now_add=True)
    action_title = models.CharField(max_length=100,blank=True,null=True)
    category = models.CharField(max_length=50,blank=True,null=True)

    def __str__(self):
        return f'{self.profile.username} - {self.action}'
