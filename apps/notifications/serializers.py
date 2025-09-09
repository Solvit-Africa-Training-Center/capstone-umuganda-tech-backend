from rest_framework import serializers
from .models import Notification, NotificationLog
from apps.users.serializers import UserSerializer
from apps.projects.serializers import ProjectSerializer

class  NotificationSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    project = ProjectSerializer(read_only=True)

    class Meta:
        model = Notification
        fields = ["id", "user", "title", "message", "notification_type", "project", "is_read", "created_at"]
        read_only_fields = ["created_at"]

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)
    
class NotificationLogSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    project = ProjectSerializer(read_only=True)

    class Meta:
        model = NotificationLog
        fields = ["id", "user", "project", "channel", "message", "status", "created_at"]
        read_only_fields = ["created_at"]

class MarkAsReadSerializer(serializers.Serializer):
    """ Serializer for marking notifications as read """
    notification_ids = serializers.ListField(
        child=serializers.IntegerField(),
        allow_empty=False
    )