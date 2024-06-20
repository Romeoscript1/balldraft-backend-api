from rest_framework import serializers
from profiles.models import Profile

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = "__all__"

# ["username","address","mobile_number", "bank", "account_number", "account_name"]
