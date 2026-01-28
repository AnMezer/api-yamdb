from rest_framework import serializers

from reviews.models import Category


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для категорий.

    Поля:
        - name
        - slug
    """
    #author = serializers.SlugRelatedField(slug_field='username',
    #                                      read_only=True)

    class Meta:
        fields = ('name', 'slug')
        model = Category
        read_only_fields = ('name', 'slug')
