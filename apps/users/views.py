from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import User, Skill, UserSkill, Badge, UserBadge
from .serializers import UserSerializer, SkillSerializer, UserSkillSerializer, BadgeSerializer, UserBadgeSerializer
from apps.projects.models import Attendance, Certificate

# -------------------------------
# User Views
# -------------------------------
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['get'])
    def profile(self, request):
        """ Get current user profile """
        user = request.user
        attended_projects = Attendance.objects.filter(user=user).count()
        Certificate_earned = Certificate.objects.filter(user=user).count()

        return Response({
            'user': UserSerializer(user, context={'request': request}).data,
            'stats': {
                'attended_projects': attended_projects,
                'Certificate_earned': Certificate_earned,
                'badges_earned': user.badges.count(),
            }
        })

class SkillViewSet(viewsets.ModelViewSet):
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer
    permission_classes = [permissions.IsAuthenticated]

class UserSkillViewSet(viewsets.ModelViewSet):
    queryset = UserSkill.objects.all()
    serializer_class = UserSkillSerializer
    permission_classes = [permissions.IsAuthenticated]

class BadgeViewSet(viewsets.ModelViewSet):
    queryset = Badge.objects.all()
    serializer_class = BadgeSerializer
    permission_classes = [permissions.IsAuthenticated]

class UserBadgeViewSet(viewsets.ModelViewSet):
    queryset = UserBadge.objects.all()
    serializer_class = UserBadgeSerializer
    permission_classes = [permissions.IsAuthenticated]
