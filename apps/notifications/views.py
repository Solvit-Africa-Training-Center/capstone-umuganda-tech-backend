from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Notification, NotificationLog
from .serializers import NotificationSerializer, NotificationLogSerializer, MarkAsReadSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self): #type: ignore
        # Handle Swagger schema generation
        if getattr(self, 'swagger_fake_view', False):
            return Notification.objects.none()
        
        user = self.request.user
        if not user.is_authenticated:
            return Notification.objects.none()
            
        # only return notifications for the current user
        return Notification.objects.filter(user=user)

    
    def get_serializer_context(self):
        return {'request': self.request}
    @swagger_auto_schema(
        operation_description="Get only unread notifications for current user",
        responses={
            200: openapi.Response('Unread notifications', examples={
                'application/json': {
                    'count': 5,
                    'notifications': [
                        {
                            'id': 1,
                            'title': 'New Project Available',
                            'message': 'A new project has been created in your area',
                            'is_read': False,
                            'created_at': '2024-01-15T10:30:00Z'
                        }
                    ]
                }
            })
        }
    )
    
    @action(detail=False, methods=['get'])
    def unread(self, request):
        """ Get only unread notifications """
        unread_notifications = self.get_queryset().filter(is_read=False)
        serializer = self.get_serializer(unread_notifications, many=True)
        return Response({
            'count': unread_notifications.count(),
            'notifications': serializer.data
        })
    
    @swagger_auto_schema(
        operation_description="Mark a single notification as read",
        responses={
            200: openapi.Response('Success', examples={
                'application/json': {
                    'message': 'Notification marked as read'
                }
            }),
            404: 'Notification not found'
        }
    )
    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        """ Mark a single notification as read """
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response({'message': 'Notification marked as read'})
    
    @swagger_auto_schema(
        operation_description="Mark all unread notifications as read for current user",
        responses={
            200: openapi.Response('Success', examples={
                'application/json': {
                    'message': '5 notifications marked as read',
                    'updated_count': 5
                }
            })
        }
    )
    @action(detail=False, methods=['post'])
    def mark_all_as_read(self, request):
        """ Mark all unread notifications as read """
        updated_count = self.get_queryset().filter(is_read=False).update(is_read=True)
        return Response({
            'message': f'{updated_count} notifications marked as read',
            'updated_count': updated_count
        })
    
    @swagger_auto_schema(
        operation_description="Mark multiple specific notifications as read",
        request_body=MarkAsReadSerializer,
        responses={
            200: openapi.Response('Success', examples={
                'application/json': {
                    'message': '3 notifications marked as read',
                    'count': 3
                }
            }),
            400: 'Invalid notification IDs'
        }
    )
    
    @action(detail=False, methods=['post'])
    def mark_multiple_as_read(self, request):
        """ Mark multiple notifications as read """
        serializer =  MarkAsReadSerializer(data=request.data)
        if serializer.is_valid():
            notification_ids = serializer.validated_data['notification_ids'] #type: ignore
            updated_count = self.get_queryset().filter(id__in=notification_ids, is_read=False).update(is_read=True)
            return Response({
                'message': f'{updated_count} notifications marked as read',
                'count': updated_count
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class NotificationLogViewSet(viewsets.ReadOnlyModelViewSet):
    """Read-only viewset for notification delivery logs.
    
    Shows SMS/Email delivery status and history for current user.
      """
    queryset = NotificationLog.objects.all()
    serializer_class = NotificationLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Get notification delivery logs for current user",
        responses={200: NotificationLogSerializer(many=True)}
    )
    
    def get_queryset(self): #type: ignore
        # Handle Swagger schema generation
        if getattr(self, 'swagger_fake_view', False):
            return NotificationLog.objects.none()
        
        user = self.request.user
        if not user.is_authenticated:
            return NotificationLog.objects.none()
            
        # only return logs for the current user
        return NotificationLog.objects.filter(user=user)



