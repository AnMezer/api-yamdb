from django.contrib.auth import get_user_model, tokens
from django.shortcuts import get_object_or_404, render
from rest_framework import permissions, viewsets, request, status
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework_simplejwt import views as simplejwtviews
    #TokenRefreshView,

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
from .services.email import sender_mail

User = get_user_model()


class TokenView(simplejwtviews.TokenObtainPairView):
    #def post():
    queryset = User.objects.all()
    # queryset = User.objects.all()


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    #serializer_class = UserSerializer

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

    def create(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)

        if self.basename == 'signup_user':
            username = serializer.initial_data.get('username', None)
            user = User.objects.filter(username=username).first()
            if serializer.is_valid():
                username = serializer.validated_data.get('username')
                email = serializer.validated_data.get('email')
                serializer.save()
                headers = self.get_success_headers(serializer.data)
                
                try:
                    sender_mail(122345, email)
                    tokens.default_token_generator.make
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
                    sender_mail(122345, user.email)
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

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
