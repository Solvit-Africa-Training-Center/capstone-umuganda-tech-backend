from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserBadgeViewSet

router = DefaultRouter()
router.register(r'user-badges', UserBadgeViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
