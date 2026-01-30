from django.conf import settings
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404, render
from rest_framework import permissions, viewsets, request
from rest_framework.pagination import LimitOffsetPagination
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from reviews.models import Category, Genre, Title, Review, Comment
from .permissions import AdminOnly
from .serializers import (
    CategorySerializer,
    GenreSerializer,
    TitleSerializer,
    UserSerializer,
    SignUpSerializer,
    ReviewSerializer,
    CommentSerializer
)

User = get_user_model()


class TokenView(TokenObtainPairView):
    #def post():
    pass
    # queryset = User.objects.all()


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    # @action()
    # def get():
    #     pass
    
    def get_serializer_class(self):
        if self.basename == 'users':
            return UserSerializer
        else:
            return SignUpSerializer

    def get_permissions(self):
        if self.basename == 'signup_user':
            return (permissions.AllowAny(),)
        elif self.basename == 'users_me':
            return (permissions.IsAuthenticated,)
        else:
            return (AdminOnly(),)

    # queryset = User.objects.all()
    # permission_classes = (permissions.IsAuthenticated)


class CategoryViewSet(viewsets.ModelViewSet):
    """Вьюсет для работы с категориями."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = LimitOffsetPagination
    # permission_classes


class GenreViewSet(viewsets.ModelViewSet):
    """Вьюсет для работы с жанрами."""

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    pagination_class = LimitOffsetPagination
    # permission_classes


class TitleViewSet(viewsets.ModelViewSet):
    """Вьюсет для работы с произведениями."""

    queryset = Title.objects.all()
    serializer_class = TitleSerializer
    pagination_class = LimitOffsetPagination
    # permission_classes


class ReviewViewSet(viewsets.ModelViewSet):
    """Вьюсет для работы с отзывами на произведения."""

    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    pagination_class = LimitOffsetPagination
    # permission_classes =


class CommentViewSet(viewsets.ModelViewSet):
    """Вьюсет для работы с комментариями на отзывы."""

    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    pagination_class = LimitOffsetPagination
    # permission_classes =
