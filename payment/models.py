from django.db import models
from accounts.models import Profile

class Deposit(models.Model):
    profile = models.ForeignKey(Profile,on_delete=models.CASCADE)
    time = models.DateTimeField(auto_now_add=True)
    amount = models.DecimalField(max_digits=20,decimal_places=5,blank=True,null=True)
    verified = models.BooleanField(default=False)
    
    def __str__(self):
        return f'Deposit'
    
    def save(self, *args, **kwargs):
        if self.verified:
            self.profile.account_balance += int(float(self.amount))
            self.profile.save()
            
            action = f'{self.profile.user.username} has deposited {self.amount}'
            action_title = 'Deposit Verified'
            self.profile.notification_set.create(profile=self.profile,action_title=action_title,action=action)
            # subject = action_title
            # body = f'Your deposit of {self.amount} to your balldraft fantasy account has been verfied'
            # send_email(subject,body,self.profile.user.email)
            
                
        return super().save(*args, **kwargs)
    

class Withdraw(models.Model):
    profile = models.ForeignKey(Profile,on_delete=models.CASCADE)
    time = models.DateTimeField(auto_now_add=True)
    amount = models.DecimalField(max_digits=20,decimal_places=5,blank=True,null=True)
    verified = models.BooleanField(default=False)
    
    def __str__(self):
        return f'Withdraw'
    
    def save(self, *args, **kwargs):
        if self.verified:
            self.profile.account_balance -= int(float(self.amount))
            self.profile.save()
           
            action = f'{self.profile.user.username} withdrawal of  N{self.amount} has been approved'
            action_title = 'Withdrawal Verified'
            self.profile.notification_set.create(profile=self.profile,action_title=action_title,action=action)
            # subject = action_title
            # body = f'Your withdrawal of {self.amount} has been verfied'
            # send_email(subject,body,self.profile.user.email)
            
        return super().save(*args, **kwargs)


class PaymentHistory(models.Model):
    profile = models.ForeignKey(Profile,on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=20,decimal_places=5,blank=True,null=True)
    payment_type =  models.CharField(max_length=200,null=True,blank=True)
    payment_date =  models.DateTimeField(auto_now_add=True)
    reason_for_payment =  models.CharField(max_length=200,null=True,blank=True)

    def __str__(self):
        return f'{self.amount} was {self.payment_type}  to / from {self.profile.username} on {self.payment_date} '
