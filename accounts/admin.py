from django.contrib import admin
from .models import User, EmailVerificationTOTP, ReasonToLeave, Referral

class OneTimePasswordAdmin(admin.ModelAdmin):
    list_display = ('user', 'otp' ,'timestamp')
    readonly_fields = ('otp',)

admin.site.register(User)
admin.site.register(EmailVerificationTOTP)
admin.site.register(ReasonToLeave)
admin.site.register(Referral)
