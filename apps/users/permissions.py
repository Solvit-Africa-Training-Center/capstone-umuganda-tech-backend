from rest_framework import permissions
from .models import User

class IsAdminUser(permissions.BasePermission):
    """Only admin users can access"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == User.Roles.ADMIN

class IsAdminOrReadOnly(permissions.BasePermission):
    """Admin can do anything, others can only read"""
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        return request.user.is_authenticated and request.user.role == User.Roles.ADMIN

class IsOwnerOrAdmin(permissions.BasePermission):
    """Users can only access their own data, admins can access all"""
    def has_object_permission(self, request, view, obj):
        if request.user.role == User.Roles.ADMIN:
            return True
        if hasattr(obj, 'user'):
            return obj.user == request.user
        return obj == request.user

class IsLeaderOrAdmin(permissions.BasePermission):
    """Leaders can access their sector data, admins can access all"""
    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.role == User.Roles.ADMIN:
            return True
        if user.role == User.Roles.LEADER:
            if hasattr(obj, 'user'):
                return obj.user.sector == user.sector
            return obj.sector == user.sector
        return False

class IsOwnerLeaderOrAdmin(permissions.BasePermission):
    """Combined permission: owner, sector leader, or admin"""
    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.role == User.Roles.ADMIN:
            return True
        if user.role == User.Roles.LEADER:
            if hasattr(obj, 'user'):
                return obj.user.sector == user.sector
            if hasattr(obj, 'sector'):
                return obj.sector == user.sector
        if hasattr(obj, 'user'):
            return obj.user == user
        return obj == user
