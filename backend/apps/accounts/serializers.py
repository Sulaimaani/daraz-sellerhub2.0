from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import User, UserProfile


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "is_active",
            "email_verified",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "is_active",
            "email_verified",
            "created_at",
            "updated_at",
        )


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    business_name = serializers.CharField(
        write_only=True, required=False, allow_blank=True
    )
    phone = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ("email", "password", "business_name", "phone")

    def create(self, validated_data):
        business_name = validated_data.pop("business_name", "")
        phone = validated_data.pop("phone", "")
        user = User.objects.create_user(
            email=validated_data["email"], password=validated_data["password"]
        )
        UserProfile.objects.create(user=user, business_name=business_name, phone=phone)
        return user
