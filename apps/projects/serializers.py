from rest_framework import serializers
from .models import Project, ProjectSkill, Attendance

# -------------------------------
# Project Skill Serializer
# -------------------------------
class ProjectSkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectSkill
        fields = ["id", "project", "skill"]

# -------------------------------
# Attendance Serializer
# -------------------------------
class AttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = ["id", "user", "project", "check_in_time", "check_out_time"]

# -------------------------------
# Project Serializer
# -------------------------------
class ProjectSerializer(serializers.ModelSerializer):
    skills = ProjectSkillSerializer(source="projectskill_set", many=True, read_only=True)

    class Meta:
        model = Project
        fields = ["id", "title", "description", "sector", "datetime", "location",
                  "required_volunteers", "picture_url", "admin", "status", "created_at", "skills"]
        read_only_fields = ["created_at"]
