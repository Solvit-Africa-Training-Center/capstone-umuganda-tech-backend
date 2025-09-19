from django.db import models
from apps.users.models import User
from apps.projects.models import Project


class Post(models.Model):
    POST_TYPE_CHOICES = [
        ("suggestion", "Suggestion"),
        ("feedback", "Feedback"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, blank=True, 
    null=True, related_name="posts")

    title = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    sector = models.CharField(max_length=255, blank=True, null=True)
    datetime = models.DateTimeField(blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    
    content = models.TextField()
    type = models.CharField(max_length=50, choices=POST_TYPE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.type} by {self.user.phone_number}"

    @property 
    def upvotes_count(self):
        return self.upvotes.count()  #type: ignore

    def has_upvoted(self, user):
        return self.upvotes.filter(user=user).exists() #type: ignore

class PostUpvote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="upvotes")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="upvotes")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "post")

    def __str__(self):
        return f"{self.user.phone_number} upvoted {self.post.id}" #type: ignore
    
class Comment(models.Model):
    user =  models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    post =  models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user.phone_number} on post {self.post.id}" #type: ignore
