from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.pagination import LimitOffsetPagination

from reviews.models import Category, Genre
from .serializers import CategorySerializer, GenreSerializer


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