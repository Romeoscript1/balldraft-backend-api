from django.contrib import admin
from .models import User, OneTimePassword, Profile, ReasonToLeave

admin.site.register(User)
admin.site.register(OneTimePassword)
admin.site.register(Profile)
admin.site.register(ReasonToLeave)