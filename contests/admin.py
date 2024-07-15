from django.contrib import admin
from contests.models import *

class ContestHistoryAdmin(admin.ModelAdmin):
    list_display = ('name')
    prepopulated_fields = {'slug':('name',) }

class PlayerAdmin(admin.ModelAdmin):
    list_display = ('name')
    prepopulated_fields = {'slug': ('name',)}



admin.site.register(ContestHistory)
admin.site.register(Player)
