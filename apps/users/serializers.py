from rest_framework import serializers
from .models import User, Skill, UserSkill, Badge, UserBadge,OTP
from django.contrib.auth import authenticate 
from rest_framework_simplejwt.tokens import RefreshToken
import re
from django.contrib.auth import get_user_model

# -------------------------------
# Skill Serializers
# -------------------------------
User=get_user_model()
class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ["id", "name"]

class UserSkillSerializer(serializers.ModelSerializer):
    skill = SkillSerializer(read_only=True)
    skill_id = serializers.PrimaryKeyRelatedField(
        queryset=Skill.objects.all(), source="skill", write_only=True
    )

    class Meta:
        model = UserSkill
        fields = ["id", "skill", "skill_id"]

# -------------------------------
# Badge Serializers
# -------------------------------
class BadgeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Badge
        fields = ["id", "name", "description", "icon_url"]

class UserBadgeSerializer(serializers.ModelSerializer):
    badge = BadgeSerializer(read_only=True)
    badge_id = serializers.PrimaryKeyRelatedField(
        queryset=Badge.objects.all(), source="badge", write_only=True
    )

    class Meta:
        model = UserBadge
        fields = ["id", "badge", "badge_id", "awarded_at"]

# -------------------------------
# User Serializer
# -------------------------------
class UserSerializer(serializers.ModelSerializer):
    skills = UserSkillSerializer(source="userskill_set", many=True, read_only=True)
    badges = UserBadgeSerializer(many=True, read_only=True)
    avatar_url = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "phone_number", "first_name", "last_name", "email", "sector", "role", "avatar_url", "skills", "badges", "created_at"]
        read_only_fields = ["created_at"]

    def get_avatar_url(self, obj):
        if obj.avatar:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.avatar.url)
            return obj.avatar.url
        return None

# --------------------------------
# Authentication Serializers
# --------------------------------
class RegisterSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(max_length=45, write_only=True)

    class Meta:
        model = User
        fields = ["first_name", "last_name", "phone_number", "role", "password", "confirm_password"]
        read_only_fields = ["created_at"]
        extra_kwargs = {
            "password": {"write_only": True}
        }

    def validate(self, data):  #type: ignore
        if data["password"] != data["confirm_password"]:
            raise serializers.ValidationError("Passwords must match")
        return data

    def create(self, validated_data):
        validated_data.pop("confirm_password")
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def validate_phone_number(self, value):
        # Rwandan phone number kuyivalidatinga
        if not re.match(r'^(\+250|250)?[0-9]{9}$', value):
            raise serializers.ValidationError("Invalid Rwandan phone number format. It should start with +250 followed by 9 digits.")
        # Normalize phone number hano
        if value.startswith('+250'):
            value = value[4:]
        elif value.startswith('250'):
            value = value[3:]
        if User.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError("Phone number already in use.")
        
        return value
class VerifyOTPSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=20)
    otp_code = serializers.CharField(max_length=6)
    password = serializers.CharField(write_only=True, required=False)

    def validate(self, attrs):
        phone_number = attrs.get('phone_number')
        otp_code = attrs.get('otp_code')

        try:
            otp = OTP.objects.filter(phone_number=phone_number, code=otp_code, is_verified=False).latest('created_at')

            if otp.is_expired():
                raise serializers.ValidationError("OTP has expired.")
        except OTP.DoesNotExist:
            raise serializers.ValidationError("Invalid OTP.")
        attrs['otp'] = otp
        return attrs

class LoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=20)
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        phone_number = attrs.get('phone_number')
        password = attrs.get('password')

        user = authenticate(username=phone_number, password=password)
        if not user:
            raise serializers.ValidationError("Invalid credentials.")
        
        if not user.is_active:
            raise serializers.ValidationError("User account is disabled.")
        attrs['user'] = user
        return attrs