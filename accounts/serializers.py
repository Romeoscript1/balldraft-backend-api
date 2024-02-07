from rest_framework import serializers
from .models import User
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed



class UserRegisterSerializer(serializers.ModelSerializer):
    password=serializers.CharField(max_length=68, min_length=8, write_only=True)
    password2=serializers.CharField(max_length=68, min_length=8, write_only=True)

    class Meta:
        model=User
        fields=['email', 'first_name', 'last_name', 'password', 'dob','password2']

    def validate(self, attrs):
        password= attrs.get('password', '')
        password2= attrs.get('password2', '')
        if password != password2:
            raise serializers.ValidationError("passwords do not match")
        return attrs
        # return super().validate(attrs)
    
    def create(self, validated_data):
        user=User.objects.create_user(
            email=validated_data['email'],
            first_name=validated_data.get('first_name'),
            last_name=validated_data.get('last_name'),
            dob=validated_data.get('dob'),
            password=validated_data.get('password')
        )
        return user
        # return super().create(validated_data)
    
class LoginSerializer(serializers.ModelSerializer):
    email=serializers.EmailField(max_length=255, min_length=6)
    password=serializers.CharField(max_length=68, write_only=True)
    full_name=serializers.CharField(max_length=255, write_only=True, required=False)
    access_token=serializers.CharField(max_length=255, write_only=True, required=False)
    refresh_token=serializers.CharField(max_length=255, write_only=True, required=False)

    class Meta:
        model=User
        fields=['email','password',
                'full_name','access_token','refresh_token'
                ]

    def validate(self, attrs):
        email=attrs.get('email')
        password=attrs.get('password')
        request=self.context.get('request')
        user = authenticate(request, email=email, password=password)
        print(user)
        if not user:
            raise AuthenticationFailed('Invalid crendentials try again')
        if not user.is_verified:
            raise AuthenticationFailed("Email is not verified")
        user_tokens=user.tokens()

        # print(user_tokens)
        response_data = {
            'email': user.email,
            'full_name': user.get_full_name,
            'access_token': user_tokens['access'],
            'refresh_token': user_tokens['refresh']
        }

        return response_data
