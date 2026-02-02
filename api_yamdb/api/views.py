from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import filters, permissions, viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework_simplejwt import views as simplejwtviews

from reviews.models import Category, Genre, Title, Review
from .permissions import (AdminOnly, ReadOnly, OwnerOrReadOnly,
                          ModeratorOrOwnerOrReadOnly)
from .viewsets import (CategoryGenreViewset, BaseTitleViewset,
                       ReviewCommentViewset)
from .serializers import (
    CategorySerializer,
    CommentSerializer,
    GenreSerializer,
    ReviewSerializer,
    SignUpSerializer,
    TitleSerializer,
    TokenSerializer,
    UserSerializer
)
from .services.email import sender_mail
from .utils.confirm_code import ConfirmationCodeService

User = get_user_model()


class TokenView(simplejwtviews.TokenViewBase):
    """Вьюсет для выдачи токенов"""

    def get_serializer_class(self):
        return TokenSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            return Response(
                serializer.validated_data,
                status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    """Вьюсет для работы с пользователями, регистрация, редакт польз."""
    queryset = User.objects.all()
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)
    http_method_names = ['get', 'post', 'patch', 'delete']
    lookup_field = 'username'

    def get_serializer_class(self):
        if self.basename != 'signup_user':
            return UserSerializer
        return SignUpSerializer

    def get_permissions(self):
        if self.basename == 'signup_user':
            return (permissions.AllowAny(),)
        elif self.action == 'me':
            return (OwnerOrReadOnly(),)
        else:
            return (AdminOnly(),)

    def create(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)

        if self.basename == 'signup_user':
            username = serializer.initial_data.get('username', None)
            user = User.objects.filter(username=username).first()
            if serializer.is_valid():
                username = serializer.validated_data.get('username')

                email = serializer.validated_data.get('email')

                serializer.save()

                user = User.objects.filter(username=username).first()
                code = ConfirmationCodeService.generate_code(user)

                headers = self.get_success_headers(serializer.data)

                try:
                    sender_mail(code, email)
                    return Response(
                        serializer.data, status=200, headers=headers
                    )
                except Exception as e:
                    return Response(
                        {'username': username,
                         'email': email,
                         'error': f'Письмо с кодом не отправлено: {str(e)}'},
                        status=status.HTTP_200_OK
                    )
            elif user and (
                    user.email == serializer.initial_data.get('email', None)):
                try:
                    code = ConfirmationCodeService.generate_code(user)
                    sender_mail(code, user.email)
                    return Response(
                        {'username': user.username,
                         'email': user.email},
                        status=status.HTTP_200_OK
                    )
                except Exception as e:
                    return Response(
                        {'error': f'Письмо с кодом не отправлено: {str(e)}'},
                        status=status.HTTP_503_SERVICE_UNAVAILABLE
                    )
            elif user and (
                    user.email != serializer.initial_data.get('email', None)):
                return Response(
                    {'error': 'Учетные данные не верны'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.validated_data,
                                status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False,
            permission_classes=(OwnerOrReadOnly),
            methods=['get', 'patch', 'delete'],
            url_path='me')
    def me(self, request):
        user = request.user

        if request.method == 'PATCH':
            serializer = self.get_serializer(user,
                                             data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors,
                                status=status.HTTP_400_BAD_REQUEST)
        elif request.method == 'DELETE':
            raise MethodNotAllowed('DELETE')

        serializer = self.get_serializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CategoryViewSet(CategoryGenreViewset):
    """Вьюсет для работы с категориями."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenreViewSet(CategoryGenreViewset):
    """Вьюсет для работы с жанрами."""

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class TitleViewSet(BaseTitleViewset):
    """Вьюсет для работы с произведениями."""

    queryset = Title.objects.all()
    serializer_class = TitleSerializer
    pagination_class = LimitOffsetPagination
    permission_classes = (AdminOnly,)
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_permissions(self):
        """Устанавливает права доступа"""
        if self.action in ['list', 'retrieve']:
            return (ReadOnly(),)
        return super().get_permissions()

    def get_queryset(self):
        """Фильтрует ответ по параметрам запроса."""
        queryset = Title.objects.all()
        params = self.request.query_params
        genre = params.get('genre', None)
        category = params.get('category', None)
        year = params.get('year', None)
        name = params.get('name', None)

        if genre:
            queryset = queryset.filter(genre__slug=genre)
        if category:
            queryset = queryset.filter(category__slug=category)
        if year:
            queryset = queryset.filter(year=year)
        if name:
            queryset = queryset.filter(name__contains=name)
        return queryset


class ReviewViewSet(ReviewCommentViewset):
    """Вьюсет для работы с отзывами к произведению <title_id>."""

    serializer_class = ReviewSerializer
    pagination_class = LimitOffsetPagination

    def get_title_id(self):
        """Определеяет ID текущего произведения."""
        return self.kwargs.get('title_id')

    def get_queryset(self):
        """Выбирает отзывы только к текущему произведению."""
        return Review.objects.filter(title_id=self.get_title_id())

    def perform_create(self, serializer):
        """Создает новый отзыв, привязывая его к текущему произведению
        и авторизованному пользователю."""
        title = get_object_or_404(Title, id=self.get_title_id())
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    """Вьюсет для работы с комментариями к отзыву <review_id>."""

    serializer_class = CommentSerializer
    pagination_class = LimitOffsetPagination
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_permissions(self):
        if self.action == 'list':
            return (ReadOnly(),)
        elif self.action in ['update', 'partial_update', 'destroy']:
            return (ModeratorOrOwnerOrReadOnly(),)
        return super().get_permissions()

    def get_review(self):
        """Определяет ID текущего отзыва."""
        review_id = self.kwargs.get('review_id')
        return get_object_or_404(Review, id=review_id)

    def get_queryset(self):
        """Выбирает комментарии только для отзыва <review_id>."""
        return self.get_review().comments.all()

    def perform_create(self, serializer):
        """Создает новый комментарий, привязывая его к отзыву и
        авторизованному пользователю."""
        review = self.get_review()
        serializer.save(author=self.request.user, review=review)
