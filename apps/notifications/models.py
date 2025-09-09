from django.db import models
from apps.users.models import User
from apps.projects.models import Project
from django.utils.html import escape

class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ("project_update", "Project Update"),
        ("new_comment", "New Comment"),
        ("project_reminder", "Project Reminder"),
        ("upvote_received", "Upvote Received"),
        ("project_created", "New Project Created")
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    title = models.CharField(max_length=255)
    message = models.TextField()
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True, blank=True, related_name="notifications")
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
    
    def __str__(self):
        return f"{escape(self.title)} - {escape(self.user.phone_number)}"
    
    @classmethod
    def create_notification(cls, user, title, message, notification_type, project=None):
        """ Helper method to create notifications """
        return cls.objects.create(
            user=user,
            title=title,
            message=message,
            notification_type=notification_type,
            project=project
        )

class NotificationLog(models.Model):
    """ This model is for SMS/Email Logging """
    CHANNEL_CHOICES = [
        ("sms", "SMS"),
        ("email", "Email"),
    ]
    STATUS_CHOICES = [
        ("sent", "Sent"),
        ("failed", "Failed"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notification_logs")
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True, blank=True, related_name="notification_logs")
    channel = models.CharField(max_length=20, choices=CHANNEL_CHOICES)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="sent")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.channel} to {escape(self.user.phone_number)} ({self.status})"
