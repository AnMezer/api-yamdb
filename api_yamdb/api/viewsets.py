from rest_framework import filters, permissions, viewsets, mixins
from rest_framework.pagination import LimitOffsetPagination

from .permissions import (AdminOnly, ListReadOnly, ReadOnly,
                          ModeratorOrOwnerOrReadOnly)


class BaseViewset(viewsets.GenericViewSet):
    """Базовый вьюсет для вьюсетов"""
    pagination_class = LimitOffsetPagination


class AdminOnlyViewset(BaseViewset):
    """Базовый вьюсет для вьюсетов с доступом только администратору"""
    permission_classes = (AdminOnly,)


class CategoryGenreViewset(mixins.ListModelMixin, mixins.CreateModelMixin,
                           mixins.DestroyModelMixin, AdminOnlyViewset):
    """Базовый вьюсет для категорий и жанров"""
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'

    def get_permissions(self):
        """Устанавливает права доступа"""
        if self.action == 'list':
            return (ListReadOnly(),)
        return super().get_permissions()


class BaseTitleViewset(viewsets.ModelViewSet, AdminOnlyViewset):
    """Базовый вьюсет для произведений"""
    http_method_names = ['get', 'post', 'patch', 'delete']


class ReviewCommentViewset(viewsets.ModelViewSet):
    """Базовый вьюсет для отзывов и комментов"""
    pagination_class = LimitOffsetPagination
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_permissions(self):
        """Устанавливает права доступа"""
        if self.action == 'list':
            return (ReadOnly(),)
        elif self.action in ['update', 'partial_update', 'destroy']:
            return (ModeratorOrOwnerOrReadOnly(),)
        return super().get_permissions()
