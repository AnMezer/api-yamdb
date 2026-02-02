from django.contrib.auth import get_user_model
from rest_framework import permissions

User = get_user_model()


class CustomBasePermission(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)


class ModeratorOrOwnerOrReadOnly(CustomBasePermission):

    def has_permission(self, request, view):
        super().has_permission(request, view)
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        super().has_object_permission(request, view, obj)
        return (
            request.user == obj.author
            or request.user.is_moder
        )


class AdminOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.is_admin

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)


class ReadOnly(CustomBasePermission):
    pass


class ListReadOnly(CustomBasePermission):

    def has_object_permission(self, request, view, obj):
        return False


class RetrievReadOnly(ReadOnly):
    pass


class IsAdminOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.method == 'GET':
            return True
        if not request.user or not request.user.is_authenticated:
            return False
        return getattr(request.user, 'role', None) == 'admin'

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)


class OwnerOrReadOnly(ModeratorOrOwnerOrReadOnly):

    def has_object_permission(self, request, view, obj):
        return False
