from django.contrib import admin
from .models import User, OneTimePassword, ReasonToLeave

class OneTimePasswordAdmin(admin.ModelAdmin):
    list_display = ('user', 'otp' ,'timestamp')
    readonly_fields = ('otp',)

admin.site.register(User)
admin.site.register(OneTimePassword)
admin.site.register(ReasonToLeave)