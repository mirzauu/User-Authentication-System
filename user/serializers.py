from rest_framework import serializers
from.models import CustomUser
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
import re

User = get_user_model()


class SignUpSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['username', 'mobile_number', 'email', 'password', 'date_of_birth']

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("A user with this username already exists.")
        if not re.match(r'^[a-zA-Z0-9]+$', value):
            raise serializers.ValidationError("Username can only contain letters and numbers.")
        return value

    def validate_mobile_number(self, value):
        if not re.match(r'^\+?1?\d{9,15}$', value):
            raise serializers.ValidationError("Enter a valid mobile number.")
        if User.objects.filter(mobile_number=value).exists():
            raise serializers.ValidationError("A user with this mobile number already exists.")
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long.")
        if not re.search(r'[A-Z]', value):
            raise serializers.ValidationError("Password must contain at least one uppercase letter.")
        if not re.search(r'[a-z]', value):
            raise serializers.ValidationError("Password must contain at least one lowercase letter.")
        if not re.search(r'\d', value):
            raise serializers.ValidationError("Password must contain at least one digit.")
        if not re.search(r'\W', value):
            raise serializers.ValidationError("Password must contain at least one special character.")
        return value

    def validate_date_of_birth(self, value):
        from datetime import date
        if value > date.today():
            raise serializers.ValidationError("Date of birth cannot be in the future.")
        return value
    
    def create(self, validated_data):
        user = User(
            username=validated_data['username'],
            mobile_number=validated_data['mobile_number'],
            email=validated_data['email'],
            date_of_birth=validated_data['date_of_birth']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

class LoginSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        try:
            user_instance = User.objects.get(username=user.username)
        except User.DoesNotExist:
            raise ValueError("User does not exist")
        token = super().get_token(user)
        print('====0',user)
        token['username'] = user.username
        return token
    
    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user
        data['username'] = user.username
        tokens = super().get_token(self.user)
        data['tokens'] = {
        'access': str(tokens.access_token),
        'refresh': str(tokens),
        }
        return data