from django.forms import SlugField
from rest_framework import serializers

from reviews.models import Category, Genre, Title, Review, Comment


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
                raise serializers.ValidationError('Необходимо указать оценку!')
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
