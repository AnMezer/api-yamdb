from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.tokens import RefreshToken

from constants.constants import (
    CHAR_FIELD_LENGTH,
    FORBIDDEN_USERNAME,
    REGEX_STAMP,
    SLUG_FIELD_LENGTH,
)
from reviews.models import Category, Comment, Genre, Review, Title

User = get_user_model()


class NameSlugSerialiser(serializers.ModelSerializer):
    """Базовый сериализатор для полей name и slug."""
    name = serializers.CharField(max_length=CHAR_FIELD_LENGTH)

    class Meta:
        fields = ('name', 'slug')
        abstract = True


class CategorySerializer(NameSlugSerialiser):
    """Сериализатор для категорий.

    Поля:
        - name
        - slug
    """
    slug = serializers.SlugField(
        max_length=SLUG_FIELD_LENGTH,
        validators=[
            RegexValidator(regex=REGEX_STAMP,
                           message=(f'Для slug можно использовать'
                                    f'только символы {REGEX_STAMP}')),
            UniqueValidator(queryset=Category.objects.all(),
                            message='Категория с таким slug уже существует.')
        ]
    )

    class Meta(NameSlugSerialiser.Meta):
        model = Category


class GenreSerializer(NameSlugSerialiser):
    """Сериализатор для жанров.

    Поля:
        - name
        - slug
    """
    slug = serializers.SlugField(
        max_length=SLUG_FIELD_LENGTH,
        validators=[
            UniqueValidator(queryset=Genre.objects.all(),
                            message='Такой slug уже существует.')
        ]
    )

    class Meta(NameSlugSerialiser.Meta):
        model = Genre


class TitleModifySerializer(serializers.ModelSerializer):
    """Сериализатор для создания и изменения произведений."""

    genre = serializers.SlugRelatedField(slug_field='slug',
                                         queryset=Genre.objects.all(),
                                         many=True, required=True)
    category = serializers.SlugRelatedField(slug_field='slug',
                                            queryset=Category.objects.all())
    name = serializers.CharField(max_length=CHAR_FIELD_LENGTH)

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'description',
                  'genre', 'category')
        read_only_fields = ('id', 'rating')

    def to_representation(self, instance):
        return TitleReadSerializer(instance, context=self.context).data


class TitleReadSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения произведений."""

    genre = GenreSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)
    name = serializers.CharField(max_length=CHAR_FIELD_LENGTH)

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'description',
                  'rating', 'genre', 'category')
        read_only_fields = ('id', 'rating')


class BaseUserSerializer(serializers.ModelSerializer):
    """Базовый сериализатор пользователей."""
    class Meta:
        model = User
        fields = ('username', 'email')

    def validate_username(self, value):
        username = value

        if username.lower() == FORBIDDEN_USERNAME:
            raise serializers.ValidationError(
                {
                    'username': 'Данное имя пользователя запрещено.'
                }
            )

        return value

    def validate(self, data):
        username = data.get('username')
        email = data.get('email')
        user = User.objects.filter(username=username).first()

        if user and user.email != email:
            raise serializers.ValidationError(
                {'error': 'Учетные данные не верны.'})

        return data


class UserSerializer(BaseUserSerializer):
    """Сериализатор для создания пользователей админом."""
    role = serializers.CharField(default=User.Role.USER)

    class Meta(BaseUserSerializer.Meta):
        fields = (BaseUserSerializer.Meta.fields
                  + ('first_name', 'last_name', 'bio', 'role'))

    def get_fields(self):
        fields = super().get_fields()
        view = self.context.get('view')

        if view and view.action == 'change_me':
            fields['role'].read_only = True
        return fields

    def validate_role(self, value):
        role = value

        if role not in [User.Role.USER, User.Role.ADMIN, User.Role.MODER]:
            raise serializers.ValidationError(
                {
                    'role': 'Данная роль запрещена.'
                }
            )

        return value


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
        if not user:
            raise serializers.ValidationError(
                {'detail': 'Пользователь не найден'}
            )
        code = user.confirmation_code.filter(is_used=False).first()
        if not code or confirmation_code != code.code:
            if code:
                code.increase_attempts
            raise serializers.ValidationError(
                {'confirmation_code': 'Неверный код'}
            )
        if code.is_valid:
            code.is_used = True
            code.save()
            refresh = RefreshToken.for_user(user)
            return {
                'token': str(refresh.access_token)
            }
        code.is_used = True
        code.save()
        raise serializers.ValidationError(
            {
                'confirmation_code': (
                    'Попытки входа с таким кодом '
                    'запрещены, запросите новый код.')
            }
        )


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для отзывов к произведениям."""

    author = serializers.StringRelatedField(
        source='author.username', read_only=True)
    title = serializers.PrimaryKeyRelatedField(read_only=True)
    score = serializers.IntegerField(
        min_value=1, max_value=10,
        error_messages={
            'min_value': 'Оценка должна быть целым числом от 1 до 10.',
            'max_value': 'Оценка должна быть целым числом от 1 до 10.'})

    class Meta:
        fields = ('id', 'text', 'author', 'pub_date', 'score', 'title')
        model = Review

    def validate(self, data):
        """
        Проверяет, что пользователь еще не оставлял отзыв на это произведение,
        """
        request = self.context.get('request')
        view = self.context.get('view')
        if request.method == 'POST':
            title_id = view.kwargs.get('title_id')
            review = Review.objects.filter(
                author=request.user, title_id=title_id)
            if review.exists():
                raise serializers.ValidationError(
                    'Вы уже оставили отзыв на это произведение.')

        return data


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор для комментариев к отзывам."""

    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        many=False
    )
    review = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        fields = ('id', 'text', 'author', 'pub_date', 'review')
        model = Comment
