from django.conf import settings
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404, render
from rest_framework import permissions, viewsets, request, filters
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
    permission_classes = (AdminOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


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
    """Вьюсет для работы с отзывами к произведению <title_id>."""

    serializer_class = ReviewSerializer
    pagination_class = LimitOffsetPagination
    # permission_classes =

    def get_title_id(self):
        """Определеяет ID текущего произведения."""
        return self.kwargs['title_id']

    def get_queryset(self):
        """Выбирает отзывы только к текущему произведению."""
        return Review.objects.filter(title=self.get_title_id())

    def perform_create(self, serializer):
        """Создает новый отзыв, привязывая его к текущему произведению
        и авторизованному пользователю."""
        serializer.save(author=self.request.user, title=self.get_title_id())


class CommentViewSet(viewsets.ModelViewSet):
    """Вьюсет для работы с комментариями к отзыву <review_id>."""

    serializer_class = CommentSerializer
    pagination_class = LimitOffsetPagination
    # permission_classes =

    def get_review_id(self):
        """Определяет ID текущего отзыва."""
        return self.kwargs['review_id']

    def get_queryset(self):
        """Выбирает комментарии только для отзыва <review_id>."""
        return Comment.objects.filter(review_id=self.get_review_id())

    def perform_create(self, serializer):
        """Создает новый комментарий, привязывая его к отзыву и
        авторизованному пользователю."""
        serializer.save(author=self.request.user,
                        review_id=self.get_review_id())
