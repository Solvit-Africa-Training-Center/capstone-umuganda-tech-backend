from django.db import models
from apps.users.models import User
from apps.projects.models import Project


class NotificationLog(models.Model):
    CHANNEL_CHOICES = [
        ("sms", "SMS"),
        ("email", "Email"),
    ]
    STATUS_CHOICES = [
        ("sent", "Sent"),
        ("failed", "Failed"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True, blank=True, related_name="notifications")
    channel = models.CharField(max_length=20, choices=CHANNEL_CHOICES)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="sent")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.channel} to {self.user.phone_number} ({self.status})"
