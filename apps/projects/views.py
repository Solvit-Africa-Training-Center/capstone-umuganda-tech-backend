from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.utils.html import escape
import re
from django.db import models
from .models import Project, ProjectSkill, Attendance, ProjectCheckinCode
from .serializers import (
    ProjectSerializer, ProjectSkillSerializer, AttendanceSerializer, ProjectCheckinCodeSerializer, CheckinSerializer
    )
from apps.notifications.utils import create_project_notification
 
def sanitize_for_notification(project):
    """ Sanitize projects data before passing to notification system """
    #  Remove path traversal characters and sanitize content
    safe_title = re.sub(r'[./\\]', '', project.title)
    safe_sector = re.sub(r'[./\\]', '', project.sector) if project.sector else ''

    # create a safe copy of project data
    return{
        'id': project.id,
        'title': escape(safe_title),
        'sector': escape(safe_sector),
        'admin': project.admin
    }

class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        # amazonq-ignore-next-line
        project = serializer.save(admin=self.request.user)
        # Create notification for new project
        safe_project_data = sanitize_for_notification(project)
        create_project_notification(safe_project_data, "project_created")
    
    def perform_update(self, serializer):
        project = serializer.save()
        # Create notification for project update
        safe_project_data = sanitize_for_notification(project)
        create_project_notification(safe_project_data, "project_update")
    

class ProjectSkillViewSet(viewsets.ModelViewSet):
    queryset = ProjectSkill.objects.all()
    serializer_class = ProjectSkillSerializer
    permission_classes = [permissions.IsAuthenticated]

class AttendanceViewSet(viewsets.ModelViewSet):
    # queryset = Attendance.objects.all()
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
