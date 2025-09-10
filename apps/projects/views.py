from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from django.utils import timezone
from django.shortcuts import get_object_or_404
from .models import Project, ProjectSkill, Attendance, ProjectCheckinCode,Certificate
from .serializers import (
    ProjectSerializer, ProjectSkillSerializer, AttendanceSerializer,CertificateSerializer, ProjectCheckinCodeSerializer, CheckinSerializer
    )
from apps.users.permissions import IsOwnerOrAdmin
from .services import CertificateService,GamificationService
class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]

class ProjectSkillViewSet(viewsets.ModelViewSet):
    queryset = ProjectSkill.objects.all()
    serializer_class = ProjectSkillSerializer
    permission_classes = [permissions.IsAuthenticated]

class AttendanceViewSet(viewsets.ModelViewSet):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
    permission_classes = [permissions.IsAuthenticated]

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def generate_qr_code(request, project_id):
    """ Generate QR code for a project (Leaders only) """
    project = get_object_or_404(Project, id=project_id)

    # Check if user is project admin (leader)
    if project.admin != request.user:
        return Response({"error": "Only project admin(leader) can generate QR code."}, status=status.HTTP_403_FORBIDDEN)
    
    # Create or get existing QR Code
    qr_code, created = ProjectCheckinCode.objects.get_or_create(project=project)
    
    serializer = ProjectCheckinCodeSerializer(qr_code, context={'request': request})
    return Response({
        'message': 'QR code generated successfully',
        'qr_code': serializer.data
    }, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def checkin(request):
    """ Check-in to a project using QR code"""
    serializer =  CheckinSerializer(data=request.data)
    if serializer.is_valid():
        qr_data = serializer.validated_data['qr_code'] #type: ignore
        project_id = qr_data['project_id']

        # heck if user already checked in
        existing_attendance =  Attendance.objects.filter(
            user=request.user,
            project_id=project_id,
            check_out_time__isnull=True
        ).first()

        if existing_attendance:
            return Response({'error': 'You have already checked in to this project.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Create attendance record
        attendance = Attendance.objects.create(
            user=request.user,
            project_id=project_id,
            check_in_time=timezone.now()
        )

        return Response({
            'message': 'Checked in successfully.',
            'attendance_id': AttendanceSerializer(attendance).data
        }, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def checkout(request):
    """ Check-out from a project """
    serializer = CheckinSerializer(data=request.data)
    if serializer.is_valid():
        qr_data = serializer.validated_data['qr_code'] #type: ignore
        project_id = qr_data['project_id']

        # Find activate attendance record
        try:
            attendance = Attendance.objects.get(
                user=request.user,
                project_id=project_id,
                check_out_time__isnull=True
            )
        except Attendance.DoesNotExist:
            return Response({'error': 'No active check-in found for this project.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Update check-out time
        attendance.check_out_time = timezone.now()
        attendance.save()

        # Auto-generate certificate if project is completed
        certificate_viewset = CertificateViewSet()
        certificate_viewset._auto_generate_certificate(request.user, attendance.project)

        # Award badges for milestones
        awarded_badges = GamificationService.award_badges(request.user)

        response_data = {
            'message': 'Checked out successfully.',
            'attendance': AttendanceSerializer(attendance).data
        }
        
        if awarded_badges:
            from apps.users.serializers import BadgeSerializer
            response_data['new_badges'] = BadgeSerializer(awarded_badges, many=True).data

        return Response(response_data, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def project_attendance(request, project_id):
    """ Get attendance records for a project"""
    project = get_object_or_404(Project, id=project_id)
    attendances = Attendance.objects.filter(project=project)

    serializer = AttendanceSerializer(attendances, many=True)
    return Response({
        'project': project.title,
        'attendances': serializer.data
    }, status=status.HTTP_200_OK)

#Certificate views

class CertificateViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CertificateSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]

    def get_queryset(self):
        if self.request.user.role == 'admin':
            return Certificate.objects.all()
        return Certificate.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['post'], url_path='generate/(?P<project_id>[^/.]+)')
    def generate_certificate(self, request, project_id=None):
        """Generate certificate for completed project"""
        project = get_object_or_404(Project, id=project_id)
        
        attendance = Attendance.objects.filter(
            user=request.user,
            project=project,
            check_out_time__isnull=False
        ).first()
        
        if not attendance:
            return Response({'error': 'You must complete attendance for this project.'}, status=status.HTTP_400_BAD_REQUEST)
        
        if project.status != 'completed':
            return Response({'error': 'Certificate can only be generated for completed projects.'}, status=status.HTTP_400_BAD_REQUEST)
        
        certificate, created = Certificate.objects.get_or_create(
            user=request.user,
            project=project
        )
        
        # Generate PDF if new certificate or no file exists
        if created or not certificate.certificate_file:
            CertificateService.generate_pdf(certificate)
        
        return Response({
            'message': 'Certificate generated successfully.' if created else 'Certificate already exists.',
            'certificate': self.get_serializer(certificate).data
        }, status=status.HTTP_200_OK)

    def _auto_generate_certificate(self, user, project):
        """Helper method for auto-generating certificates"""
        if project.status == 'completed':
            certificate, created = Certificate.objects.get_or_create(
                user=user,
                project=project
            )
            if created or not certificate.certificate_file:
                CertificateService.generate_pdf(certificate)
            return certificate
