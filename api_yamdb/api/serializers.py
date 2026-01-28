from rest_framework import serializers

from reviews.models import Category, Genre


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