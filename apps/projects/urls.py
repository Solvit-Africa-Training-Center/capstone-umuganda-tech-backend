from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ProjectViewSet, ProjectSkillViewSet, AttendanceViewSet, CertificateViewSet,
    generate_qr_code, checkin, checkout, project_attendance, get_qr_code,
    follow_leader, unfollow_leader
    )
from . import file_views
from .api_docs import api_overview


router = DefaultRouter()
router.register(r'', ProjectViewSet, basename='project')
router.register(r'project-skills', ProjectSkillViewSet)
router.register(r'attendances', AttendanceViewSet)
router.register(r'certificates', CertificateViewSet, basename='certificate')

urlpatterns = [
    path('', include(router.urls)),
    path('api-overview/', api_overview, name='api-overview'),
    path('projects/<int:project_id>/generate_qr_code/', generate_qr_code, name='generate_qr_code'),
    path('projects/<int:project_id>/get_qr_code/', get_qr_code, name='get_qr_code'),
    path('checkin/', checkin, name='checkin'),
    path('checkout/', checkout, name='checkout'),
    path('projects/<int:project_id>/attendance/', project_attendance, name='project_attendance'),
    path('projects/<int:project_id>/upload-image/', file_views.upload_project_image, name='upload_project_image'),
    path('projects/<int:project_id>/delete-image/', file_views.delete_project_image, name='delete_project_image'),

    path('leaders/<int:leader_id>/follow/', follow_leader, name='follow_leader'),
    path('leaders/<int:leader_id>/unfollow/', unfollow_leader, name='unfollow_leader'),

]


