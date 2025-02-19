from rest_framework import serializers
from .models import User


class UserRegisterSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ("username", "email", "password", "password2")
        extra_kwargs = {
            "password": {"write_only": True},
            # "password2": {"write_only": True},
        }

    def validate(self, data):
        if data.get("password") != data.get("password2"):
            raise serializers.ValidationError("Passwords must be match!")
        return data

    def create(self, validated_data):
        del validated_data["password2"]
        user = User.objects.create_user(**validated_data)
        return user


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField()
    new_password = serializers.CharField()

class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)