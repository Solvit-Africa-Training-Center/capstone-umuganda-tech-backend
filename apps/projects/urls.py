from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ProjectViewSet, ProjectSkillViewSet, AttendanceViewSet, CertificateViewSet,
    generate_qr_code, checkin, checkout, project_attendance
)

router = DefaultRouter()
router.register(r'projects', ProjectViewSet)
router.register(r'project-skills', ProjectSkillViewSet)
router.register(r'attendances', AttendanceViewSet)
router.register(r'certificates', CertificateViewSet, basename='certificate')

urlpatterns = [
    path('', include(router.urls)),
    path('projects/<int:project_id>/generate_qr_code/', generate_qr_code, name='generate_qr_code'),
    path('checkin/', checkin, name='checkin'),
    path('checkout/', checkout, name='checkout'),
    path('projects/<int:project_id>/attendance/', project_attendance, name='project_attendance')
]


