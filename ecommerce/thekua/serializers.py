from rest_framework import serializers
from .models import PendingUser,Role,User,Profile
from .utils import generate_otp,send_otp
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken

User=get_user_model()

class SignupRequestSerializer(serializers.Serializer):
    email=serializers.EmailField(required=False)
    mobile_no=serializers.CharField(required=False)

    def validate(self,data):
        if not data.get("email") and not data.get("mobile_no"):
            raise serializers.ValidationError("Email or mobile number is required")
        return data
    
    def create(self,validated_data):
        otp=generate_otp()

        pending_user=PendingUser.objects.create(
            email=validated_data.get("email"),
            mobile_no=validated_data.get("mobile_no"),
            otp=otp
        )

        send_otp(validated_data.get("email") or validated_data.get("mobile.no"),otp)

        return pending_user
    
class OTPVerifySerializer(serializers.Serializer):
    session_id=serializers.UUIDField()
    otp=serializers.CharField(max_length=6)
    username=serializers.CharField()
    password=serializers.CharField(write_only=True)

    def validate(self, data):
        try:
            pending=PendingUser.objects.get(session_id=data["session_id"],otp=data["otp"])
        except PendingUser.DoesNotExist:
            raise serializers.ValidationError("Invalid OTP")
        if pending.is_expired():
            raise serializers.ValidationError("OTP expired")
        if User.objects.filter(username=data["username"]).exists():
            raise serializers.ValidationError("Username already taken")
        
        data["pending_user"] = pending
        return data
    
    def create(self, validated_data):
        pending=validated_data["pending_user"]

        user=User.objects.create(
            username=validated_data["username"],
            email=pending.email,
            mobile_no=pending.mobile_no,
        )

        user.set_password(validated_data["password"])
        user.save()

        Role.objects.create(
            user=user,
            role=Role.CUSTOMER,
            active=True
        )

        pending.delete()
        return user
    
class LoginSerializer(serializers.Serializer):
    username=serializers.CharField()
    password=serializers.CharField(write_only=True)

    def validate(self, data):
        username = data.get("username")
        password = data.get("password")

        user = authenticate(username=username, password=password)

        if not user:
            raise serializers.ValidationError("Invalid username or password")

        if not user.is_active:
            raise serializers.ValidationError("User account is inactive")

        refresh = RefreshToken.for_user(user)

        return {
            "user":user,
            "user_id": user.id,
            "username": user.username,
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }
    
class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model=Profile
        fields=["name","address","pin_code","state","country","profile_pic"]