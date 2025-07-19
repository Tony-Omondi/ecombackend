from rest_framework import serializers
from .models import CustomUser, Profile, ShippingAddress, OTPVerification
from django.core.exceptions import ValidationError
from django.utils import timezone

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = CustomUser
        fields = ['email', 'password']

    def validate_email(self, value):
        if CustomUser.objects.filter(email=value).exists():
            raise ValidationError('This email is already registered.')
        return value

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            is_verified=False
        )
        return user

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['first_name', 'last_name', 'contact_number', 'profile_picture', 'bio', 'gender', 'birthday']
        read_only_fields = ['created_at', 'updated_at']

class ShippingAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingAddress
        fields = ['id', 'title', 'street_address', 'city', 'county', 'postal_code', 'phone_number', 'is_default', 'created_at']
        read_only_fields = ['created_at']

    def validate(self, data):
        if data.get('is_default'):
            # Ensure only one default address per user
            user = self.context['request'].user
            if ShippingAddress.objects.filter(user=user, is_default=True).exclude(id=self.instance.id if self.instance else None).exists():
                raise ValidationError({'is_default': 'Another address is already set as default.'})
        return data

class OTPSerializer(serializers.ModelSerializer):
    class Meta:
        model = OTPVerification
        fields = ['code']

    def validate_code(self, value):
        otp = self.instance
        if otp.expires_at < timezone.now():
            raise ValidationError('OTP has expired.')
        if otp.code != value:
            raise ValidationError('Invalid OTP code.')
        return value

class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not CustomUser.objects.filter(email=value).exists():
            raise ValidationError('No user found with this email.')
        return value

class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    new_password = serializers.CharField(write_only=True, min_length=8)