from django.db import models
from apps.users.models import User, Skill
import uuid
import qrcode
from io import BytesIO
from django.core.files import File
from django.utils import timezone
from datetime import timedelta
from django.utils.html import escape


# -------------------------------
# Project Category
# -------------------------------
class ProjectCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


# -------------------------------
# Projects
# -------------------------------
class Project(models.Model):
    STATUS_CHOICES = [
        ("planned", "Planned"),
        ("ongoing", "Ongoing"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    sector = models.CharField(max_length=100)
    category = models.ForeignKey(ProjectCategory, on_delete=models.SET_NULL, null=True, blank=True)
    datetime = models.DateTimeField()
    location = models.CharField(max_length=255, blank=True, null=True)
    required_volunteers = models.PositiveIntegerField(blank=True, null=True)
    image = models.ImageField(upload_to='project/', blank=True, null=True)
    admin = models.ForeignKey(User, on_delete=models.CASCADE, related_name="projects")
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default="planned")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class ProjectSkill(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="project_skills")
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name="projects")

    class Meta:
        unique_together = ("project", "skill")


# -------------------------------
# Attendance
# -------------------------------
class Attendance(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="attendances")
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="attendances")
    check_in_time = models.DateTimeField()
    check_out_time = models.DateTimeField(blank=True, null=True)

    class Meta:
        # allow multiple attendance records per user per project
        # This suports recurring project and multiple sessions
        # unique_together = ("user", "project")
        ordering = ['-check_in_time']


# -------------------------------
# QR Code Check-In
# -------------------------------
class ProjectCheckinCode(models.Model):
    project = models.OneToOneField(Project, on_delete=models.CASCADE, related_name="checkin_code")
    code = models.CharField(max_length=255, unique=True)  # random/hashed token
    expires_at = models.DateTimeField()
    qr_image = models.ImageField(upload_to='qr_code/', blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = str(uuid.uuid4())
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(hours=24)
        super().save(*args, **kwargs)

        # Generate QR code
        if not self.qr_image:
            self.generate_qr_code()

    def generate_qr_code(self):
        qr_data = f"umuganda_checkin:{self.project.id}:{self.code}" #type: ignore
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(qr_data)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format="PNG") #type: ignore

        filename = f'qr_project_{self.project.id}.png'  #type: ignore
        self.qr_image.save(filename, File(buffer), save=False)
        self.save(update_fields=['qr_image'])
    
    def is_expired(self):
        return timezone.now() > self.expires_at
    
    def __str__(self):
        return f"QR Code for {escape(self.project.title)}"



# -------------------------------
# Certificates
# -------------------------------
class Certificate(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="certificates")
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="certificates")
    file_url = models.TextField()  # link to PDF/Cloud file
    issued_at = models.DateTimeField(auto_now_add=True)


# -------------------------------
# Project Impact
# -------------------------------
class ProjectImpact(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="impacts")
    metric_name = models.CharField(max_length=100)   # e.g., "trees_planted"
    value = models.IntegerField()
    unit = models.CharField(max_length=50)           # e.g., "trees", "kg"

    def __str__(self):
        return f"{self.project.title}: {self.value} {self.unit} ({self.metric_name})"
