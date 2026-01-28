from django.forms import SlugField
from rest_framework import serializers

from reviews.models import Category, Genre, Title


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
    """Сериализатор для категорий.

    Поля:
        - name
        - slug
    """
    class Meta:
        fields = ('name', 'slug')
        model = Genre
        read_only_fields = ('name', 'slug')


class TitleSerializer(serializers.ModelSerializer):
    """Сериализатор для произведений.
    """
    genre = GenreSerializer(many=True)
    category = CategorySerializer()

    class Meta:
        fields = '__all__'
        model = Title
        read_only_fields = ('id', 'rating')
