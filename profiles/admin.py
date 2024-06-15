from django.contrib import admin
from profiles.models import Profile
# ContestEntry

class ProfileAdmin(admin.ModelAdmin):
    readonly_fields = ('id',)

admin.site.register(Profile)
# admin.site.register(ContestEntry)