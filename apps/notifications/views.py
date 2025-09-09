from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Notification, NotificationLog
from .serializers import NotificationSerializer, NotificationLogSerializer, MarkAsReadSerializer

class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self): #type: ignore
        # only return notifications for the current user
        return Notification.objects.filter(user=self.request.user)
    
    def get_serializer_context(self):
        return {'request': self.request}
    
    @action(detail=False, methods=['get'])
    def unread(self, request):
        """ Get only unread notifications """
        unread_notifications = self.get_queryset().filter(is_read=False)
        serializer = self.get_serializer(unread_notifications, many=True)
        return Response({
            'count': unread_notifications.count(),
            'notifications': serializer.data
        })
    
    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        """ Mark a single notification as read """
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response({'message': 'Notification marked as read'})
    
    @action(detail=False, methods=['post'])
    def mark_all_as_read(self, request):
        """ Mark all unread notifications as read """
        updated_count = self.get_queryset().filter(is_read=False).update(is_read=True)
        return Response({
            'message': f'{updated_count} notifications marked as read',
            'updated_count': updated_count
        })
    
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
    """ Read-only viewset for notification logs (SMS/EMAIL) """
    queryset = NotificationLog.objects.all()
    serializer_class = NotificationLogSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self): #type: ignore
        # only return logs for the current user
        return NotificationLog.objects.filter(user=self.request.user)


