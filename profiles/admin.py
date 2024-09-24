from django.contrib import admin
from profiles.models import *
# ContestEntry

class ProfileAdmin(admin.ModelAdmin):
    readonly_fields = ('id',)

admin.site.register(Profile)
admin.site.register(Notification)
admin.site.register(Bonus)
admin.site.register(Penalty)
admin.site.register(Deposit)
admin.site.register(Withdraw)
admin.site.register(TransactionHistory)
admin.site.register(Payment)



# admin.site.register(ContestEnt
# admin.site.register(Profile)ry)