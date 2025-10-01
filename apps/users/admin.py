from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Skill, UserSkill, Badge, UserBadge
from django.utils import timezone

# -------------------------------
# Custom User Admin
# -------------------------------
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('phone_number', 'first_name', 'last_name', 'email', 'sector', 'role', 'is_leader_approved', 'leader_application_date', 'is_staff', 'is_active', 'created_at')
    list_filter = ('is_staff', 'is_active', 'sector', 'role', 'is_leader_approved')
    search_fields = ('phone_number', 'first_name', 'last_name', 'email')
    ordering = ('phone_number',)
    readonly_fields = ('created_at', 'leader_application_date', 'approval_date')
    actions = ['approve_leaders', 'reject_leaders']
    
    fieldsets = (
        (None, {'fields': ('phone_number', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'email', 'sector', 'role')}),
        ('Leader Approval', {'fields': ('is_leader_approved', 'leader_verification_document', 'leader_application_date', 'approval_date', 'approved_by')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important Dates', {'fields': ('last_login', 'created_at')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone_number', 'password1', 'password2', 'is_staff', 'is_active', 'is_verified')}
        ),
    )

    def approve_leaders(self, request, queryset):
        updated = queryset.filter(role='leader', is_leader_approved=False).update(
            is_leader_approved=True, 
            approval_date=timezone.now(),
            approved_by=request.user
        )
        self.message_user(request, f'{updated} leaders have been approved.')

    def reject_leaders(self, request, queryset):
        updated = queryset.filter(role='leader').update(is_leader_approved=False)
        self.message_user(request, f'{updated} leaders have been rejected.')

# Skills Admin
@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)

@admin.register(UserSkill)
class UserSkillAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'skill')
    search_fields = ('user__phone_number', 'skill__name')
    list_filter = ('skill',)

# -------------------------------
# Badges Admin
# -------------------------------
@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description', 'icon_url')
    search_fields = ('name', 'description')

@admin.register(UserBadge)
class UserBadgeAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'badge', 'awarded_at')
    search_fields = ('user__phone_number', 'badge__name')
    list_filter = ('badge',)
    readonly_fields = ('awarded_at',)
