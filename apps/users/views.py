from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from .models import User, Skill, UserSkill, Badge, UserBadge
from .serializers import UserSerializer, SkillSerializer, UserSkillSerializer, BadgeSerializer, UserBadgeSerializer
from apps.projects.models import Attendance, Certificate

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

    @action(detail=False, methods=['post'])
    def generate_images(self, request):
        """Generate badge images (Admin only)"""
        if request.user.role != 'admin':
            return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)
        
        try:
            from apps.projects.services import GamificationService
            GamificationService.create_default_badges()
            return Response({
                'message': 'Badge images generated successfully',
                'badges_created': Badge.objects.count()
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'])
    def setup_default(self, request):
        """Setup default badges with images (Admin only)"""
        if request.user.role != 'admin':
            return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)
        
        try:
            from apps.projects.services import GamificationService
            GamificationService.create_default_badges()
            badges = Badge.objects.all()
            return Response({
                'message': 'Default badges setup completed',
                'badges': BadgeSerializer(badges, many=True).data
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserBadgeViewSet(viewsets.ModelViewSet):
    queryset = UserBadge.objects.all()
    serializer_class = UserBadgeSerializer
    permission_classes = [permissions.IsAuthenticated]
