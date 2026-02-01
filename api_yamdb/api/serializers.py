from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from django.forms import SlugField
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainSerializer
from rest_framework.validators import UniqueValidator

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


class TokenSerializer(TokenObtainSerializer):
    #username = serializers.CharField()
    confirmation_code = serializers.CharField()

    class Meta(TokenObtainSerializer):
        exlude = ('password',)
        #fields = ('username', 'confirmation_code')
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
            reviewer = Review.objects.filter(
                author=request.user, title_id=title_id)
            if reviewer.exists():
                raise serializers.ValidationError(
                    'Вы уже оставили отзыв на это произведение.')

        return data


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор для комментариев к отзывам."""

    author = serializers.StringRelatedField(
        source='author.username', read_only=True)
    review_id = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        fields = ('id', 'text', 'author', 'pub_date', 'review_id')
        model = Comment
