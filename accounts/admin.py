from django.contrib import admin
from .models import User, OneTimePassword, Profile, ReasonToLeave

class OneTimePasswordAdmin(admin.ModelAdmin):
    list_display = ('user', 'otp' ,'timestamp')
    readonly_fields = ('otp',)

class ProfileAdmin(admin.ModelAdmin):
    readonly_fields = ('id',)

admin.site.register(User)
admin.site.register(OneTimePassword)
admin.site.register(Profile)
admin.site.register(ReasonToLeave)