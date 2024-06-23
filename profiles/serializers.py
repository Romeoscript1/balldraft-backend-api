from rest_framework import serializers
from django.contrib.auth import get_user_model
from profiles.models import Profile, Notification, Referral,Payment, Withdraw

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

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'profile', 'action', 'time', 'action_title', 'read']
        read_only_fields = ['id', 'profile', 'time']
        

class ReferralSerializer(serializers.ModelSerializer):
    referred_by = serializers.CharField(write_only=True)

    class Meta:
        model = Referral
        fields = ['id', 'profile', 'date_joined', 'referred_by']
        read_only_fields = ['id', 'profile', 'date_joined']

    def create(self, validated_data):
        referred_by_username = validated_data.pop('referred_by')
        try:
            referrer_profile = Profile.objects.get(username=referred_by_username)
        except Profile.DoesNotExist:
            raise serializers.ValidationError({'referred_by': 'Profile with this username does not exist.'})

        referral = Referral.objects.create(profile=referrer_profile, **validated_data)

        # Update referrer profile's referral_people count
        referrer_profile.referral_people += 1
        referrer_profile.save()
        
        return referral
    
    
class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'ngn_amount', 'reference', 'status', 'created_at', 'updated_at']
        read_only_fields = ['id', 'reference', 'status', 'created_at', 'updated_at']


class PaymentVerifySerializer(serializers.Serializer):
    reference = serializers.CharField(max_length=100)
    
    
class WithdrawSerializer(serializers.ModelSerializer):
    class Meta:
        model = Withdraw
        fields = [
            'id', 'profile', 'time', 'bank_name', 'account_number',
            'ngn_amount', 'verified', 'comment', 'reference'
        ]
        read_only_fields = ['id', 'profile', 'time', 'verified']