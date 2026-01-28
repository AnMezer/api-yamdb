from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404, render
from rest_framework import permissions, viewsets
from rest_framework.pagination import LimitOffsetPagination
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from reviews.models import Category, Genre, Title
from .serializers import CategorySerializer, GenreSerializer, TitleSerializer

User = get_user_model()


class TokenViewSet(TokenObtainPairView, TokenRefreshView):
    pass
    #queryset = User.objects.all()


class UserViewSet(viewsets.ModelViewSet):
    pass
    # queryset = User.objects.all()
    # permission_classes = (permissions.IsAuthenticated)


class CategoryViewSet(viewsets.ModelViewSet):
    """Вьюсет для работы с категориями.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = LimitOffsetPagination
    # permission_classes


class GenreViewSet(viewsets.ModelViewSet):
    """Вьюсет для работы с категориями.
    """
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    pagination_class = LimitOffsetPagination
    # permission_classes


class TitleViewSet(viewsets.ModelViewSet):
    """Вьюсет для работы с категориями.
    """
    queryset = Title.objects.all()
    serializer_class = TitleSerializer
    pagination_class = LimitOffsetPagination
    # permission_classes
