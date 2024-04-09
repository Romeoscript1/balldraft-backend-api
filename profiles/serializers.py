from rest_framework import serializers
from profiles.models import Profile

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = "__all__"

class UserNameUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['username']

class MobileNumberSerializer(serializers.Serializer):
    mobile_number = serializers.CharField(max_length=15)

class AddressSerializer(serializers.Serializer):
    address = serializers.CharField(max_length=255)
    country = serializers.CharField(max_length=100)
    state = serializers.CharField(max_length=100)
    city = serializers.CharField(max_length=100)
    zip_code = serializers.CharField(max_length=20)

class EmailChangeSerializer(serializers.Serializer):
    new_email = serializers.EmailField(max_length=255)