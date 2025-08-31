from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProjectViewSet, ProjectSkillViewSet, AttendanceViewSet

router = DefaultRouter()
router.register(r'projects', ProjectViewSet)
router.register(r'project-skills', ProjectSkillViewSet)
router.register(r'attendances', AttendanceViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
