from rest_framework import serializers
from .models import Project, ProjectSkill, Attendance,ProjectCheckinCode, ProjectCategory,Certificate

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
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = ["id", "title", "description", "sector", "datetime", "location",
                  "required_volunteers", "image_url", "admin", "status", "created_at", "skills"]
        read_only_fields = ["created_at"]

    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None

# -------------------------------
# QR Code Serializers
# -------------------------------

class ProjectCheckinCodeSerializer(serializers.ModelSerializer):
    qr_image_url = serializers.SerializerMethodField()
    is_expired = serializers.SerializerMethodField()

    class Meta:
        model =  ProjectCheckinCode
        fields = ["id","project", "code", "expires_at", "qr_image_url", "is_expired"]
        read_only_fields = ["code", "expires_at"]


    def get_qr_image_url(self, obj):
        if obj.qr_image:
            return self.context['request'].build_absolute_uri(obj.qr_image.url)
        return None
    
    def get_is_expired(self, obj):
        return obj.is_expired()
    
class CheckinSerializer(serializers.Serializer):
    qr_code = serializers.CharField(max_length=255)

    def validate_qr_code(self, value):
        try:
            # Parse QR code format: "umuganda_checkin:project_id:code"
            parts = value.split(':')
            if len(parts) != 3 or parts[0] != "umuganda_checkin":
                raise serializers.ValidationError("Invalid QR code format.")
            
            project_id = int(parts[1])
            code = parts[2]

            checkin_code = ProjectCheckinCode.objects.get(project_id=project_id, code=code)

            if checkin_code.is_expired():
                raise serializers.ValidationError("This QR code has expired.")
            
        except (ValueError, ProjectCheckinCode.DoesNotExist):
            raise serializers.ValidationError("Invalid QR code.")
        
        return {
            'project_id': project_id,
            'code': code,
            'checkin_code': checkin_code
        }


#Generating certificate Serializer when User complished specific project

class CertificateSerializer(serializers.ModelSerializer):
    project_title = serializers.CharField(source='project.title', read_only=True)
    user_name = serializers.SerializerMethodField()
    certificate_url = serializers.SerializerMethodField()

    class Meta:
        model = Certificate
        fields = ["id", "user", "project", "project_title", "user_name", "certificate_url", "file_url", "issued_at"]
        read_only_fields = ["issued_at"]

    def get_user_name(self, obj):
        return f"{obj.user.first_name or ''} {obj.user.last_name or ''}".strip() or obj.user.phone_number
    
    def get_certificate_url(self, obj):
        # Try PDF file first, fallback to file_url
        if obj.certificate_file:
            return self.context['request'].build_absolute_uri(obj.certificate_file.url)
        return obj.file_url
