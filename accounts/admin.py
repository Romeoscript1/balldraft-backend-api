from django.contrib import admin
from .models import User, OneTimePassword, ReasonToLeave, Referral

class OneTimePasswordAdmin(admin.ModelAdmin):
    list_display = ('email', 'otp' ,'created_at', 'expires_at')
    readonly_fields = ('otp','created_at', 'expires_at')

admin.site.register(User)
admin.site.register(OneTimePassword)
admin.site.register(ReasonToLeave)
admin.site.register(Referral)
