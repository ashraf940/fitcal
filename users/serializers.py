# users/serializers.py
from rest_framework import serializers
from .models import User
from .models import SocialAccount


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ["email", "name", "password"]

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        user = User.objects.create(**validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "name", "is_active"]


# 👇 yeh do serializers add karo (Swagger ke liye zaroori hain)
class ResendOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()


class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=10)

class AppleAuthSerializer(serializers.Serializer):
    identity_token = serializers.CharField()
    nonce = serializers.CharField(required=False, allow_blank=True)