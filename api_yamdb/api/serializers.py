from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.validators import UniqueValidator

from constants.constants import (
    CHAR_FIELD_LENGTH,
    FORBIDDEN_USERNAME,
    REGEX_STAMP,
    SLUG_FIELD_LENGTH,
)
from reviews.models import Category, Genre, Title, Review, Comment
from .utils.confirm_code import ConfirmationCodeService

User = get_user_model()


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для категорий.

    Поля:
        - name
        - slug
    """
    name = serializers.CharField(max_length=CHAR_FIELD_LENGTH)
    slug = serializers.SlugField(
        max_length=SLUG_FIELD_LENGTH,
        validators=[
            RegexValidator(regex=REGEX_STAMP,
                           message=f'Для slug можно использовать только символы {REGEX_STAMP}'),
            UniqueValidator(queryset=Category.objects.all(),
                            message='Категория с таким slug уже существует.')
        ]
    )

    class Meta:
        fields = ('name', 'slug')
        model = Category


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор для жанров.

    Поля:
        - name
        - slug
    """
    name = serializers.CharField(max_length=CHAR_FIELD_LENGTH)
    slug = serializers.SlugField(
        max_length=SLUG_FIELD_LENGTH,
        validators=[
            UniqueValidator(queryset=Genre.objects.all(),
                            message='Жанр с таким slug уже существует.'),
        ]
    )

    class Meta:
        fields = ('name', 'slug')
        model = Genre


class TitleSerializer(serializers.ModelSerializer):
    """Сериализатор для произведений."""

    genre = serializers.SlugRelatedField(slug_field='slug',
                                         queryset=Genre.objects.all(),
                                         many=True)
    category = serializers.SlugRelatedField(slug_field='slug',
                                            queryset=Category.objects.all())
    name = serializers.CharField(max_length=CHAR_FIELD_LENGTH)

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'description',
                  'rating', 'genre', 'category')
        read_only_fields = ('id', 'rating')

    def to_representation(self, instance):
        """Заменяет слаги на объекты"""

        representation = super().to_representation(instance)
        representation['genre'] = GenreSerializer(instance.genre.all(),
                                                  many=True).data
        representation['category'] = CategorySerializer(instance.category).data

        return representation


class BaseUserSerializer(serializers.ModelSerializer):
    """Базовый сериализатор пользователей."""
    class Meta:
        model = User
        fields = ['username', 'email']

    def validate_username(self, value):
        username = value

        if username.lower() == FORBIDDEN_USERNAME:
            raise serializers.ValidationError(
                {
                    'username': 'Данное имя пользователя запрещено.'
                }
            )

        return value


class UserSerializer(BaseUserSerializer):
    """Сериализатор для создания пользователей админом."""
    role = serializers.CharField(default=User.Role.USER)

    class Meta(BaseUserSerializer.Meta):
        fields = (BaseUserSerializer.Meta.fields
                  + ['first_name', 'last_name', 'bio', 'role'])

    def validate_role(self, value):
        role = value

        if role not in [User.Role.USER, User.Role.ADMIN, User.Role.MODER]:
            raise serializers.ValidationError(
                {
                    'role': 'Данная роль запрещена.'
                }
            )

        return value

    def get_fields(self):
        fields = super().get_fields()
        view = self.context.get('view')

        if view and view.action == 'me':
            fields['role'].read_only = True
        return fields


class UserMeSerializer(BaseUserSerializer):
    """Сериализатор для пользователей."""

    class Meta(BaseUserSerializer.Meta):
        fields = (BaseUserSerializer.Meta.fields
                  + ['first_name', 'last_name', 'bio', 'role'])


class SignUpSerializer(BaseUserSerializer):
    """Сериализатор для регистрации пользователей."""
    class Meta(BaseUserSerializer.Meta):
        pass


class TokenSerializer(serializers.Serializer):
    """Кастомный сериализатор для выдачи токенов."""
    username = serializers.CharField()
    confirmation_code = serializers.CharField()

    def validate(self, attrs):
        username = attrs.get('username')
        confirmation_code = attrs.get('confirmation_code')

        user = get_object_or_404(User, username=username)

        if not ConfirmationCodeService.verify_code(user, confirmation_code):
            raise serializers.ValidationError(
                {'confirmation_code': 'Неверный код'}
            )

        refresh = RefreshToken.for_user(user)
        return {
            'access': str(refresh.access_token)
        }


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для отзывов к произведениям."""

    author = serializers.StringRelatedField(
        source='author.username', read_only=True)
    title = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        fields = ('id', 'text', 'author', 'pub_date', 'score', 'title')
        model = Review

    def validate(self, data):
        """
        Валидириует набор данных перед созданием отзыва.

        Проверяет, что пользователь еще не оставлял отзыв на это произведение,
        и что оценка есть, и это число из диапазона 1..10.
        """
        request = self.context.get('request')
        if request.method == 'POST':
            reviewer = Review.objects.filter(
                author=request.user, title=data['title_id'])
            if reviewer.exists():
                raise serializers.ValidationError(
                    'Вы уже оставили отзыв на это произведение.')

            score = data.get('score')
            if score is None:
                raise serializers.ValidationError(
                    'Необходимо указать оценку!')
            elif not isinstance(score, int):
                raise serializers.ValidationError(
                    'Оценка должна быть целым числом.')
            elif score < 1 or score > 10:
                raise serializers.ValidationError(
                    'Оценка должна быть целым числом от 1 до 10.')

        return data


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор для комментариев к отзывам."""

    author = serializers.StringRelatedField(
        source='author.username', read_only=True)
    review_id = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        fields = ('id', 'text', 'author', 'pub_date', 'review_id')
        model = Comment
