from rest_framework import filters, mixins, permissions, viewsets
from rest_framework.pagination import LimitOffsetPagination

from .permissions import (
    AdminOnly,
    ModeratorOrOwnerOrReadOnly,
)


class PaginationViewset(viewsets.GenericViewSet):
    """Добавляет пагинацию."""
    pagination_class = LimitOffsetPagination


class AdminOnlyViewset(PaginationViewset):
    """Базовый вьюсет для вьюсетов с доступом только администратору"""
    permission_classes = (permissions.IsAuthenticated, AdminOnly,)


class SlugNameViewset(mixins.ListModelMixin, mixins.CreateModelMixin,
                      mixins.DestroyModelMixin, AdminOnlyViewset):
    """Базовый вьюсет для моделей с полями 'name' и 'slug'."""
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'

    def get_permissions(self):
        """Устанавливает права доступа"""
        if self.action == 'list':
            return (permissions.IsAuthenticatedOrReadOnly(),)
        return super().get_permissions()


class RestrictedMethodsViewset(viewsets.ModelViewSet, AdminOnlyViewset):
    """Базовый вьюсет ограниченный по методам."""
    http_method_names = ['get', 'post', 'patch', 'delete']


class ReviewCommentViewset(viewsets.ModelViewSet):
    """Базовый вьюсет для отзывов и комментов"""
    pagination_class = LimitOffsetPagination
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_permissions(self):
        """Устанавливает права доступа"""
        if self.action == 'list':
            return (permissions.IsAuthenticatedOrReadOnly(),)
        elif self.action in ('update', 'partial_update', 'destroy'):
            return (ModeratorOrOwnerOrReadOnly(),)
        return super().get_permissions()
