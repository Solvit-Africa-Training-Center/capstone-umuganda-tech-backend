from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count
from .models import Project, ProjectSkill, Attendance, ProjectCheckinCode,Certificate
from .serializers import (
    ProjectSerializer, ProjectSkillSerializer, AttendanceSerializer,CertificateSerializer, ProjectCheckinCodeSerializer, CheckinSerializer
    )
from apps.users.permissions import IsOwnerOrAdmin
from .services import CertificateService
from django.db import models
from apps.notifications.utils import create_project_notification

class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):  #type: ignore
        queryset = Project.objects.all()

        # Search functionality
        search = self.request.query_params.get('search', None)  #type: ignore
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search) |
                Q(location__icontains=search) |
                Q(sector__icontains=search)
            )

        # Filter by status
        status_filter = self.request.query_params.get('status', None) #type: ignore
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        # Filter by Location
        location = self.request.query_params.get('location', None) #type: ignore
        if location:
            queryset = queryset.filter(location__icontains=location)

        # Filter by date range
        date_from = self.request.query_params.get('date_from', None) #type: ignore
        date_to = self.request.query_params.get('date_to', None) #type: ignore
        if date_from:
            queryset = queryset.filter(datetime__gte=date_from)
        if date_to:
            queryset = queryset.filter(datetime__lte=date_to)

        return queryset.order_by('-created_at')

    def perform_create(self, serializer):
        project = serializer.save(admin=self.request.user)
        create_project_notification(project, "project_created")
    
    def perform_update(self, serializer):
        project = serializer.save()
        create_project_notification(project, "project_update")

    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """ Dashboard statistics for frontend """
        total_projects = Project.objects.count()
        active_projects = Project.objects.filter(status='ongoing').count()
        completed_projects = Project.objects.filter(status='completed').count()
        total_volunteers = Attendance.objects.values('user').distinct().count()

        # Recent projects
        recent_projects = Project.objects.order_by('-created_at')[:5]
        return Response({
            'status':  {
                'total_projects': total_projects,
                'active_projects': active_projects,
                'completed_projects': completed_projects,
                'total_volunteers': total_volunteers,
            },
                'recent_projects': ProjectSerializer(recent_projects, many=True, context={'request': request}).data

        })
    
    @action(detail=False, methods=['get'])
    def my_projects(self, request):
        """ List of projects created by current user """
        user = request.user
        if user.role == 'leader':
            projects = Project.objects.filter(admin=user)
        else:
            # Get project user has attended 
            attended_project_ids = Attendance.objects.filter(user=user).values_list('project_id', flat=True)
            projects = Project.objects.filter(id__in=attended_project_ids)

        serializer = self.get_serializer(projects, many=True)
        return Response(serializer.data)
    

class ProjectSkillViewSet(viewsets.ModelViewSet):
    queryset = ProjectSkill.objects.all()
    serializer_class = ProjectSkillSerializer
    permission_classes = [permissions.IsAuthenticated]

class AttendanceViewSet(viewsets.ModelViewSet):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self): # type: ignore
        """ Filter attendance records based on user permissions """
        user = self.request.user
        # Users can only see their own attendance records
        # Leaders can see attendance for their projects
        if user.role == 'leader': #type: ignore
            # leaders can see attendance for projects
            return Attendance.objects.filter(
                models.Q(user=user) | 
                models.Q(project__admin=user)
                )
        else:
            # Volunteers can only see their own attendance
            return Attendance.objects.filter(user=user)
        
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

        # Check if user already checked in
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
            'attendance': AttendanceSerializer(attendance).data
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

        # Find active attendance record
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

        return Response({
            'message': 'Checked out successfully.',
            'attendance': AttendanceSerializer(attendance).data
        }, status=status.HTTP_200_OK)
    
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

    def get_queryset(self):  #type: ignore
        if self.request.user.role == 'admin':   #type: ignore
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

# Remove the duplicate functions at the bottom of the file
