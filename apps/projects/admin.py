from django.contrib import admin
from .models import (
    ProjectCategory, Project, ProjectSkill,
    Attendance, ProjectCheckinCode, Certificate, ProjectImpact
)

# -------------------------------
# Project Category Admin
# -------------------------------
@admin.register(ProjectCategory)
class ProjectCategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description')
    search_fields = ('name', 'description')

# -------------------------------
# Projects Admin
# -------------------------------
@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'sector', 'category', 'admin', 'status', 'datetime', 'created_at')
    list_filter = ('status', 'sector', 'category')
    search_fields = ('title', 'sector', 'location', 'admin__phone_number')
    readonly_fields = ('created_at',)

# -------------------------------
# Project Skills Admin
# -------------------------------
@admin.register(ProjectSkill)
class ProjectSkillAdmin(admin.ModelAdmin):
    list_display = ('id', 'project', 'skill')
    search_fields = ('project__title', 'skill__name')
    list_filter = ('skill',)

# -------------------------------
# Attendance Admin
# -------------------------------
@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'project', 'check_in_time', 'check_out_time')
    search_fields = ('user__phone_number', 'project__title')
    list_filter = ('project',)

# -------------------------------
# Project Check-in Code Admin
# -------------------------------
@admin.register(ProjectCheckinCode)
class ProjectCheckinCodeAdmin(admin.ModelAdmin):
    list_display = ('id', 'project', 'code', 'expires_at')
    search_fields = ('project__title', 'code')

# -------------------------------
# Certificates Admin
# -------------------------------
@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'project', 'file_url', 'issued_at')
    search_fields = ('user__phone_number', 'project__title')
    readonly_fields = ('issued_at',)

# -------------------------------
# Project Impact Admin
# -------------------------------
@admin.register(ProjectImpact)
class ProjectImpactAdmin(admin.ModelAdmin):
    list_display = ('id', 'project', 'metric_name', 'value', 'unit')
    search_fields = ('project__title', 'metric_name')
    list_filter = ('metric_name',)
