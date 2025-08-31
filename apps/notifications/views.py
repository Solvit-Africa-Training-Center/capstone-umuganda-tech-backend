from rest_framework import viewsets, permissions
from .models import NotificationLog
from .serializers import UserBadgeSerializer

class UserBadgeViewSet(viewsets.ModelViewSet):
    queryset = NotificationLog.objects.all()
    serializer_class = UserBadgeSerializer
    permission_classes = [permissions.IsAuthenticated]
