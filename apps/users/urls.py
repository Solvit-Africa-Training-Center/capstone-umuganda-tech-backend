from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, SkillViewSet, UserSkillViewSet, BadgeViewSet, UserBadgeViewSet
from . import auth_views

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'skills', SkillViewSet)
router.register(r'user-skills', UserSkillViewSet)
router.register(r'badges', BadgeViewSet)
router.register(r'user-badges', UserBadgeViewSet)

urlpatterns = [
    path("", include(router.urls)),

    path('auth/register/', auth_views.register, name='register'),
    path('auth/verify-otp/', auth_views.verify_otp, name='verify-otp'),
    path('auth/login/', auth_views.login, name='login'),
    path('auth/resend-otp/', auth_views.resend_otp, name='resend-otp'),
]
