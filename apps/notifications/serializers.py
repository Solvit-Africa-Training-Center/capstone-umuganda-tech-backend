from rest_framework import serializers
from .models import NotificationLog  # if you track badges as notifications

class UserBadgeSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationLog
        fields = ["id", "user", "badge", "awarded_at"]
        read_only_fields = ["awarded_at"]
