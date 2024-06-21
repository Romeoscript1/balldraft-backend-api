from rest_framework import serializers
from profiles.models import Profile

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = "__all__"

# ["username","address","mobile_number", "bank", "account_number", "account_name"]

class EmailChangeSerializer(serializers.Serializer):
    new_email = serializers.EmailField(max_length=255)