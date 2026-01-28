from rest_framework import permissions

from constants.constants import USERS_ROLES


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
            or request.user == USERS_ROLES[1]
        )


class AdminOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user == USERS_ROLES[2]

    def has_object_permission(self, request, view, obj):
        return request.user == USERS_ROLES[2]
