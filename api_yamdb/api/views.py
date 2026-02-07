from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework_simplejwt import views as simplejwtviews

from reviews.models import Category, Genre, Review, Title
from users.models import VerifyCode

from .filters import TitleFilter
from .permissions import AdminOnly
from .serializers import (
    CategorySerializer,
    CommentSerializer,
    GenreSerializer,
    ReviewSerializer,
    SignUpSerializer,
    TitleModifySerializer,
    TitleReadSerializer,
    TokenSerializer,
    UserSerializer,
)
from .services.email import sender_mail
from .utils.code_generator import GeneratingCodeService
from .viewsets import (
    PublicationViewset,
    RestrictedMethodsViewset,
    SlugNameViewset,
)

User = get_user_model()


class TokenView(simplejwtviews.TokenViewBase):
    """Вьюсет для выдачи токенов"""

    def get_serializer_class(self):
        return TokenSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            return Response(
                serializer.validated_data
            )


class UserViewSet(viewsets.ModelViewSet):
    """Вьюсет для работы с пользователями, регистрация, редакт польз."""
    queryset = User.objects.all()
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)
    http_method_names = ['get', 'post', 'patch', 'delete']
    lookup_field = 'username'

    def get_serializer_class(self):
        if self.basename != 'signup':
            return UserSerializer
        return SignUpSerializer

    def get_permissions(self):
        if self.basename == 'signup':
            return (permissions.AllowAny(),)
        elif self.action in ['me', 'change_me', 'delete_for_me_not_allowed']:
            return (permissions.IsAuthenticated(),)
        else:
            return (permissions.IsAuthenticated(), AdminOnly(),)

    @action(detail=False,
            permission_classes=(permissions.IsAuthenticated,),
            methods=['get'],
            url_path='me')
    def me(self, request):
        user = request.user
        serializer = self.get_serializer(user)
        return Response(serializer.data)

    @me.mapping.patch
    def change_me(self, request):
        user = request.user
        serializer = self.get_serializer(user, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)

    @me.mapping.delete
    def delete_for_me_not_allowed(self, request):
        """Перехватываю delete запрос, иначе его перехватит users."""
        raise MethodNotAllowed('DELETE')

    def create(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)

        if self.basename == 'signup':
            username = request.data.get('username')
            if serializer.is_valid():
                username = serializer.validated_data.get('username')

                email = serializer.validated_data.get('email')

                serializer.save()

                user = User.objects.filter(username=username).first()
                code = GeneratingCodeService.generate_code()

                VerifyCode.objects.create(user=user, code=code)

                headers = self.get_success_headers(serializer.data)

                try:
                    sender_mail(code, email)
                    return Response(serializer.data, headers=headers)
                except Exception as e:
                    return Response(
                        {'username': username,
                         'email': email,
                         'error': f'Письмо с кодом не отправлено: {str(e)}'}
                    )
            else:
                user = User.objects.filter(username=username).first()
                if user and (
                        user.email == serializer.initial_data.get('email',
                                                                  None)):
                    try:
                        code = VerifyCode.objects.filter(
                            user=user, is_used=False).values('code')
                        if not code:
                            code = GeneratingCodeService.generate_code()
                            VerifyCode.objects.create(user=user, code=code)

                        sender_mail(code, user.email)

                        return Response(
                            {'username': user.username,
                                'email': user.email}
                        )

                    except Exception as e:
                        return Response(
                            {'error': (
                                f'Письмо с кодом не отправлено: {str(e)}')},
                            status=status.HTTP_503_SERVICE_UNAVAILABLE
                        )
        else:
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CategoryViewSet(SlugNameViewset):
    """Вьюсет для работы с категориями."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenreViewSet(SlugNameViewset):
    """Вьюсет для работы с жанрами."""

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class TitleViewSet(RestrictedMethodsViewset):
    """Вьюсет для работы с произведениями."""

    queryset = Title.objects.all()
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, AdminOnly,)
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filterset_class = TitleFilter

    def get_serializer_class(self):
        """Выбирает сериализатор в зависимости от метода запроса."""
        if self.request.method == 'GET':
            return TitleReadSerializer
        return TitleModifySerializer

    def get_permissions(self):
        """Устанавливает права доступа"""
        if self.action in ('list', 'retrieve'):
            return (permissions.IsAuthenticatedOrReadOnly(),)
        return super().get_permissions()


class ReviewViewSet(PublicationViewset):
    """Вьюсет для работы с отзывами к произведению <title_id>."""

    serializer_class = ReviewSerializer
    pagination_class = LimitOffsetPagination

    def get_title(self):
        """Возвращает объект текущего произведения."""
        title_id = self.kwargs.get('title_id')
        return get_object_or_404(Title, id=title_id)

    def get_queryset(self):
        """Выбирает отзывы только к текущему произведению."""
        return self.get_title().reviews.all()

    def perform_create(self, serializer):
        """Создает новый отзыв, привязывая его к текущему произведению
        и авторизованному пользователю."""
        title = self.get_title()
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(PublicationViewset):
    """Вьюсет для работы с комментариями к отзыву <review_id>."""

    serializer_class = CommentSerializer
    pagination_class = LimitOffsetPagination

    def get_review(self):
        """Возвращает объект текущего отзыва."""
        review_id = self.kwargs.get('review_id')
        title_id = self.kwargs.get('title_id')
        return get_object_or_404(Review, id=review_id, title=title_id)

    def get_queryset(self):
        """Выбирает комментарии только для текущего отзыва."""
        return self.get_review().comments.all()

    def perform_create(self, serializer):
        """Создает новый комментарий, привязывая его к отзыву и
        авторизованному пользователю."""
        review = self.get_review()
        serializer.save(author=self.request.user, review=review)
