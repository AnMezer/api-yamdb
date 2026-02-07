from django.contrib.auth import get_user_model
from rest_framework import permissions

User = get_user_model()


class CustomBasePermission(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS


class ModeratorOrOwnerOrReadOnly(CustomBasePermission):

    def has_permission(self, request, view):
        super().has_permission(request, view)
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return (
            request.user == obj.author
            or request.user.is_superuser
            or request.user.role == User.Role.ADMIN
            or request.user.role == User.Role.MODER
        )


class AdminOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.user.is_admin

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)
