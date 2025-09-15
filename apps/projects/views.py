from rest_framework import viewsets, permissions, status, filters
from django_filters.rest_framework import DjangoFilterBackend
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
from datetime import datetime, timedelta


from .services import CertificateService,GamificationService
class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]

    # basic filter
    # filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    # filterset_fields = ['status', 'location']
    # search_fields = ['title', 'description', 'location']


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
    
    @action(detail=False, methods=['get'])
    def discover(self, request):
        """ Smart project discovery based on user profile and preferences """
        user =  request.user

        # Nearby Projects (based on user`s sector or provided loction)
        location = request.query_params.get('location')
        if not location and user.sector:
            location = user.sector

        if location:
            nearby = Project.objects.filter(location__icontains=location, status__in=['planned', 'ongoing']).exclude(admin=user)[:5]

        else:
            nearby = Project.objects.filter(status__in=['planned', 'ongoing']).exclude(admin=user)[:5]

        # Trending projects (most attended recently)
        trending = Project.objects.annotate(
            attendance_count=Count('attendances')
        ).filter(
            status='ongoing',
            datetime__gte=timezone.now() - timedelta(days=30)
        ).order_by('-attendance_count')[:5]

        # Urgent projects (happenning soon)
        urgent = Project.objects.filter(
            datetime__gte=timezone.now(), datetime__lte=timezone.now() + timedelta(days=7), status='planned'
        ).order_by('datetime')[:5]

        # Recent projects (newly created)
        recent = Project.objects.filter(
            status='planned', created_at__gte=timezone.now() - timedelta(days=7)
        ).order_by('-created_at')[:5]

        return Response({
            'nearby': ProjectSerializer(nearby, many=True, context={'request': request}).data,
            'trending': ProjectSerializer(trending, many=True, context={'request': request}).data,
            'urgent': ProjectSerializer(urgent, many=True, context={'request': request}).data,
            'recent': ProjectSerializer(recent, many=True, context={'request': request}).data,
              })
    @action(detail=False, methods=['get'])
    def search_suggestions(self, request):
        """ Search suggections for autocomplete functionality """
        query = request.query_params.get('q', '')

        if len(query) < 2:
            return Response({'suggestions': []})
        
        # Location suggetions
        locations = Project.objects.filter(
            location__icontains=query
        ).values_list('location', flat=True).distinct()[:5]

        #  Project title suggetions
        titles = Project.objects.filter(
            title__icontains=query
        ).values_list('title', flat=True).distinct()[:5]

        # Sector suggestions 
        sectors = Project.objects.filter(
            sector__icontains=query
        ).values_list('sector', flat=True).distinct()[:5]
        
        return Response({
           'suggestion': {
               'locations': list(set(locations)),
                'titles': list(titles),
                'sectors': list(set(sectors))
             }
        })
    
    @action(detail=False, methods=['get'])
    def sorted_projects(self, request):
        """ Get projects with advanced sorting """
        queryset = Project.objects.all()

        # apply existing filter first
        search = request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search) |
                Q(location__icontains=search) |
                Q(sector__icontains=search)
            )

        status_filter = request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        location = request.query_params.get('location')
        if location:
            queryset = queryset.filter(location__icontains=location)

        # Advanced sorting 
        sort_by = request.query_params.get('sort_by', 'created_at')
        order = request.query_params.get('order', 'desc')

        # Annotate with calculated fields for sorting
        queryset = queryset.annotate(
            volunteer_count=Count('attendances_user', distinct=True),
            days_until_event=timezone.now() - models.F('datetime')
        )

        # Apply sorting
        sort_options = {
            'created_at': 'created_at',
            'datetime': 'datetime',
            'title': 'title',
            'volunteer_count': 'volunteer_count',
            'required_volunteers': 'required_volunteers',
            'urgency': 'datetime',  #sort by how soon the event is
        }
        
        sort_field = sort_options.get(sort_by, 'created_at')

        if order == 'desc':
            sort_field = f'-{sort_field}'

        queryset = queryset.order_by(sort_field)

        # pagination
        page_size = int(request.query_params.get('page_size', 10))
        page = int(request.query_params.get('page', 1))

        start = (page - 1) * page_size
        end = start + page_size

        total_count = queryset.count()
        projects = queryset[start:end]

        return Response ({
            'count': total_count,
            'page': page,
            'page_size': page_size,
            'total_pages': (total_count + page_size - 1) // page_size,
            'results': ProjectSerializer(projects, many=True, context={'request': request}).data
        })

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
