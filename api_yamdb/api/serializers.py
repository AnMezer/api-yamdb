from django.contrib.auth import get_user_model
from django.forms import SlugField
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from reviews.models import Category, Genre, Title, Review, Comment

User = get_user_model()


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для категорий.

    Поля:
        - name
        - slug
    """

    class Meta:
        fields = ('name', 'slug')
        model = Category
        read_only_fields = ('name', 'slug')


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор для жанров.

    Поля:
        - name
        - slug
    """

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


class UserSerializer(BaseUserSerializer):
    """Сериализатор для пользователей."""
    class Meta(BaseUserSerializer.Meta):
        fields = (BaseUserSerializer.Meta.fields
            + ['first_name', 'last_name', 'bio', 'role']
        )


class SignUpSerializer(serializers.ModelSerializer):
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

    author = serializers.StringRelatedField(source='author.username')

    class Meta:
        fields = ('id', 'text', 'author', 'pub_date', 'score', 'title_id')
        model = Review


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор для комментариев к отзывам."""

    author = serializers.StringRelatedField(source='author.username')

    class Meta:
        fields = ('id', 'text', 'author', 'pub_date', 'review_id')
        model = Comment
