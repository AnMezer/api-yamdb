from django.contrib.auth import get_user_model
from django.forms import SlugField
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.core.validators import RegexValidator

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from constants.constants import FORBIDDEN_USERNAME
from reviews.models import Category, Genre, Title, Review, Comment
from constants.constants import (SLUG_FIELD_LENGTH,
                                 REGEX_STAMP,
                                 CHAR_FIELD_LENGTH)

User = get_user_model()


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для категорий.

    Поля:
        - name
        - slug
    """
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
            UniqueValidator(queryset=Category.objects.all(),
                            message='Категория с таким slug уже существует.'),
        ]
    )

    class Meta:
        fields = ('name', 'slug')
        model = Genre
        read_only_fields = ('name', 'slug')


class TitleSerializer(serializers.ModelSerializer):
    """Сериализатор для произведений."""

    genre = GenreSerializer(many=True)
    category = CategorySerializer()

    class Meta:
        fields = '__all__'
        model = Title
        read_only_fields = ('id', 'rating')


class BaseUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email']

    def validate_username(self, value):
        username = value

        if username.lower() == FORBIDDEN_USERNAME:
            raise serializers.ValidationError(
                {
                    'detail': 'Данное имя пользователя запрещено.'
                }
            )

        return value


class UserSerializer(BaseUserSerializer):
    """Сериализатор для пользователей."""
    class Meta(BaseUserSerializer.Meta):
        fields = (BaseUserSerializer.Meta.fields
            + ['first_name', 'last_name', 'bio', 'role']
        )


class SignUpSerializer(BaseUserSerializer):
    class Meta(BaseUserSerializer.Meta):
        pass


class TokenSerializer(TokenObtainPairSerializer):
    #confirmation_code = default_token_generator.check_token()

    class Meta:
        fields = ('username', 'confirmation_code')
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        #token['name'] = user.name
        # ...

        return token


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
