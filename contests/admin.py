from django.contrib import admin
from contests.models import Contest, ContestCategory, ContestLevel

class ContestCategoryAdmin(admin.ModelAdmin):
    list_display = ('name')
    prepopulated_fields = {'slug':('name',) }

class ContestLevelAdmin(admin.ModelAdmin):
    list_display = ('level')
    prepopulated_fields = {'slug': ('level',)}

class ContestAdmin(admin.ModelAdmin):
    list_display = ('title')
    prepopulated_fields = {'slug':('title',) }

admin.site.register(ContestLevel)
admin.site.register(Contest)
admin.site.register(ContestCategory)