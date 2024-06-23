from rest_framework import serializers
from django.contrib.auth import get_user_model
from profiles.models import Profile, Notification

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['username', 'full_name', 'dob', 'email', 'address', 'mobile_number', 'bank', 'account_number', 'account_name', 'account_balance', 'pending_balance']

class EmailChangeSerializer(serializers.Serializer):
    new_email = serializers.EmailField(max_length=255)
    
    def validate_new_email(self, value):
        User = get_user_model()
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is already in use.")
        return value

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'profile', 'action', 'time', 'action_title', 'read']
        read_only_fields = ['id', 'profile', 'time']