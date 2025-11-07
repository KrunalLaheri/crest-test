from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "username", "role", "is_active", "date_joined"]
        read_only_fields = ["id", "date_joined"]


class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[
            UniqueValidator(
                queryset=User.objects.all(), message="A user with this email already exists."
            )
        ],
    )
    username = serializers.CharField(
        required=True,
        validators=[
            UniqueValidator(
                queryset=User.objects.all(), message="A user with this username already exists."
            )
        ],
    )
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={"input_type": "password"},
    )
    password2 = serializers.CharField(
        write_only=True, required=True, style={"input_type": "password"}, label="Confirm Password"
    )

    class Meta:
        model = User
        fields = ["email", "username", "password", "password2", "role"]
        extra_kwargs = {"role": {"required": False}}

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop("password2")
        user = User.objects.create_user(**validated_data)
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        required=True, write_only=True, style={"input_type": "password"}
    )

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        if email and password:
            user = authenticate(
                request=self.context.get("request"), username=email, password=password
            )

            if not user:
                raise serializers.ValidationError(
                    "Unable to log in with provided credentials.", code="authorization"
                )

            if not user.is_active:
                raise serializers.ValidationError("User account is disabled.", code="authorization")

            attrs["user"] = user
        else:
            raise serializers.ValidationError(
                "Must include 'email' and 'password'.", code="authorization"
            )

        return attrs


class TokenObtainPairResponseSerializer(serializers.Serializer):
    access = serializers.CharField(help_text="Access token for authentication")
    refresh = serializers.CharField(help_text="Refresh token for obtaining new access tokens")
    user = UserSerializer(read_only=True, help_text="User profile information")

    class Meta:
        fields = ["access", "refresh", "user"]
