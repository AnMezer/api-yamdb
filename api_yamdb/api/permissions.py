from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import permissions

from constants.constants import USERS_ROLES

User = get_user_model()


class ModeratorOrOwnerOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user == obj.author
            or (
                User.objects.get(username=request.user).values('role')
                == settings.MODERATOR_ROLE
            )
        )


class AdminOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            User.objects.get(username=request.user).values('role')
            == settings.ADMIN_ROLE
        )

    def has_object_permission(self, request, view, obj):
        return (
            User.objects.get(username=request.user).values('role')
            == settings.ADMIN_ROLE
        )
