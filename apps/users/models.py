from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone
import random
from  datetime import timedelta
from django.conf import settings
from django.core.mail import send_mail
from .managers import UserManager
# -------------------------------
# User Model
# -------------------------------
class User(AbstractBaseUser, PermissionsMixin):
    class Roles(models.TextChoices):
        ADMIN= "admin" , "Admin"
        LEADER= "leader" , "Leader"
        VOLUNTEER= "volunteer" , "Volunteer"
    phone_number = models.CharField(max_length=20, unique=True)
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(max_length=255, blank=True, null=True)
    sector = models.CharField(max_length=100, blank=True, null=True)
    role=models.CharField(max_length=50, choices=Roles.choices, default='VOLUNTEER' )

    # Django auth flags
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default= False)
    is_verified= models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = "phone_number"
    REQUIRED_FIELDS = []

    def __str__(self):
        return f"{self.first_name or ''} {self.last_name or ''} ({self.phone_number})"


# -------------------------------
# Skills
# -------------------------------
class Skill(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class UserSkill(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="user_skills")
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name="skill_users")

    class Meta:
        unique_together = ("user", "skill")


# -------------------------------
# Badges & Gamification
# -------------------------------
class Badge(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    icon_url = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class UserBadge(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="badges")
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE, related_name="users")
    awarded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "badge")

# ------------------------------------------
# OTP Model for Authentication
# ------------------------------------------

class OTP(models.Model):
    phone_number = models.CharField(max_length=20)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(minutes=5)
    @classmethod
    def generate_otp(cls, phone_number):
        code = str(random.randint(100000, 999999))
        return cls.objects.create(phone_number=phone_number, code=code)
    
    def __str__(self):
        return f"OTP for {self.phone_number}: {self.code}"
    