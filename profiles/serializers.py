from rest_framework import serializers
from django.contrib.auth import get_user_model
from profiles.models import Profile, Notification,Payment, Withdraw, TransactionHistory

class ProfileSerializer(serializers.ModelSerializer):
    last_login = serializers.DateTimeField(source='user.last_login', read_only=True)
    recent_deposit_time = serializers.CharField(read_only=True)
    recent_deposit_amount = serializers.CharField(read_only=True)
    total_points = serializers.FloatField(read_only=True)  # Removed the `source` parameter

    class Meta:
        model = Profile
        fields = [
            'id', 'username', 'address', 'mobile_number', 'bank', 'account_number', 
            'account_name', 'referral_people', 'referred_by', 'account_balance', 
            'pending_balance', 'country', 'state', 'city', 'zip_code', 'image',
            'last_login', 'recent_deposit_time', 'recent_deposit_amount', 'total_points'
        ]
        read_only_fields = ['id', 'referral_people', 'referred_by', 'account_balance', 
                            'pending_balance', 'last_login', 'recent_deposit_time', 
                            'recent_deposit_amount', 'total_points']

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

class UserActivitySerializer(serializers.Serializer):
    last_login = serializers.DateTimeField()
    recent_deposit_time = serializers.CharField()
    recent_deposit_amount = serializers.CharField()
    total_points = serializers.FloatField()

class HelpSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100, required=True)
    email = serializers.EmailField(required=True)
    subject = serializers.CharField(max_length=150, required=True)
    message = serializers.CharField(required=True, max_length=2000)

class TransactionHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = TransactionHistory
        fields = ['id', 'profile', 'action', 'time', 'action_title', 'category']
        read_only_fields = ['id', 'profile', 'action', 'time', 'action_title', 'category']

