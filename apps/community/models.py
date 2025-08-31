from django.db import models
from apps.users.models import User
from apps.projects.models import Project


class Post(models.Model):
    POST_TYPE_CHOICES = [
        ("suggestion", "Suggestion"),
        ("feedback", "Feedback"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, blank=True, null=True, related_name="posts")
    content = models.TextField()
    type = models.CharField(max_length=50, choices=POST_TYPE_CHOICES)
    upvotes = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.type} by {self.user.phone_number}"
