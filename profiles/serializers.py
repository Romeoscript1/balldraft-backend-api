from rest_framework import serializers
from django.contrib.auth import get_user_model
from profiles.models import Profile

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = "__all__"

class EmailChangeSerializer(serializers.Serializer):
    new_email = serializers.EmailField(max_length=255)
    
    def validate_new_email(self, value):
        User = get_user_model()
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is already in use.")
        return value
