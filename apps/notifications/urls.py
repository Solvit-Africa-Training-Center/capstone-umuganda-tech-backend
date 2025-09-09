from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import NotificationLogViewSet, NotificationViewSet

router = DefaultRouter()
router.register(r'notifications', NotificationViewSet, basename='notification')
router.register(r'logs', NotificationLogViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
