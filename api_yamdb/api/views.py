from django.contrib.auth import get_user_model, tokens
from django.shortcuts import get_object_or_404, render
from rest_framework import filters, permissions, viewsets, request, status, mixins
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework_simplejwt import views as simplejwtviews
# TokenRefreshView,

from reviews.models import Category, Genre, Title, Review, Comment
from .permissions import (AdminOnly, ListReadOnly,
                          RetrievReadOnly, ReadOnly, IsAdminOrReadOnly, StaffOrOwnerOrReadOnly)
from .serializers import (
    CategorySerializer,
    CommentSerializer,
    GenreSerializer,
    ReviewSerializer,
    SignUpSerializer,
    TitleSerializer,
    TokenSerializer,
    UserSerializer,
)
from .services.email import sender_mail
from .utils.confirm_code import ConfirmationCodeService

User = get_user_model()


class TokenView(simplejwtviews.TokenObtainPairView):
    # def post():
    queryset = User.objects.all()

    def get_serializer_class(self):
        return TokenSerializer
    # serializer_class = TokenSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    # serializer_class = UserSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)

    def get_serializer_class(self):
        if self.basename != 'signup_user':
            return UserSerializer
        else:
            return SignUpSerializer

    def get_permissions(self):
        if self.basename == 'signup_user':
            return (permissions.AllowAny(),)
        elif self.basename == 'users_me':
            return (permissions.IsAuthenticated(),)
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
                    return Response(serializer.data, status=200, headers=headers)
                except Exception as e:
                    return Response(
                        {'username': username,
                         'email': email,
                         'error': f'Письмо с кодом не отправлено: {str(e)}'},
                        status=status.HTTP_200_OK
                    )
            elif user and user.email == serializer.initial_data.get('email', None):
                try:
                    code = ConfirmationCodeService.generate_code(user)
                    sender_mail(34324, user.email)
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
            elif user and user.email != serializer.initial_data.get('email', None):
                return Response(
                    {'error': 'Учетные данные не верны'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        if self.basename == 'users':
            super().create(self, request, *args, **kwargs)
            # serializer.is_valid()
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # queryset = User.objects.all()
    # permission_classes = (permissions.IsAuthenticated)


class CategoryViewSet(mixins.ListModelMixin, mixins.CreateModelMixin,
                      mixins.DestroyModelMixin, viewsets.GenericViewSet):
    """Вьюсет для работы с категориями."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = LimitOffsetPagination
    permission_classes = (AdminOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'

    def get_permissions(self):
        if self.action == 'list':
            return (ListReadOnly(),)
        return super().get_permissions()


class GenreViewSet(mixins.ListModelMixin, mixins.CreateModelMixin,
                   mixins.DestroyModelMixin, viewsets.GenericViewSet):
    """Вьюсет для работы с жанрами."""

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    pagination_class = LimitOffsetPagination
    permission_classes = (AdminOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'

    def get_permissions(self):
        if self.action == 'list':
            return (ListReadOnly(),)
        return super().get_permissions()


class TitleViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin,
                   mixins.DestroyModelMixin, viewsets.GenericViewSet):
    """Вьюсет для работы с произведениями."""

    queryset = Title.objects.all()
    serializer_class = TitleSerializer
    pagination_class = LimitOffsetPagination
    # permission_classes = (permissions.IsAuthenticatedOrReadOnly, )
    permission_classes = (AdminOnly,)
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_permissions(self):
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


class ReviewViewSet(viewsets.ModelViewSet):
    """Вьюсет для работы с отзывами к произведению <title_id>."""

    serializer_class = ReviewSerializer
    pagination_class = LimitOffsetPagination
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_permissions(self):
        if self.action == 'list':
            return (ReadOnly(),)
        elif self.action in ['update', 'partial_update', 'destroy']:
            return (StaffOrOwnerOrReadOnly(),)
        return super().get_permissions()

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
            return (StaffOrOwnerOrReadOnly(),)
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
