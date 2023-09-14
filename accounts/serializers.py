from rest_framework import serializers
from .models import User


class UserRegisterSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField()

    class Meta:
        model = User
        fields = ("username", "email", "password", "password2")
        extra_kwargs = {
            "password": {"write_only": True},
            "password2": {"write_only": True},
        }
    def validate(self, data):
        if data.get("password") != data.get("password2"):
            raise serializers.ValidationError("Passwords must be match!")
        return data
