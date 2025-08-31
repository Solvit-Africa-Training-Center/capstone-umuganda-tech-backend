from rest_framework import serializers
from .models import User, Skill, UserSkill, Badge, UserBadge

# -------------------------------
# Skill Serializers
# -------------------------------
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
    badges = UserBadgeSerializer(source="badges", many=True, read_only=True)

    class Meta:
        model = User
        fields = ["id", "phone_number", "first_name", "last_name", "email", "sector", "skills", "badges", "created_at"]
        read_only_fields = ["created_at"]
