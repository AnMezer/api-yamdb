from constants.constants import USERS_ROLES
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator


class User(AbstractUser):
    pass
    # bio = models.TextField()
    # role = models.Choices(s)


class Title(models.Model):
    """Класс для работы с произведениями."""

    pass
    # name = models.TextField()
    # year = models.IntegerField()
    # # Формируется как усреднённая оценка произведения всеми пользователями.
    # rating = models.IntegerField()
    # description = models.TextField()
    # genre_id = models.ManyToManyField(Genre, )  # сделать доп.таблицу
    # category_id = models.ManyToManyField(Category, )  # сделать доп.таблицу


class Review(models.Model):
    """Класс для работы с отзывами на произведения."""

    text = models.TextField()
    author_id = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='review_author')
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)
    # Оценка произведению - целое число от 1 до 10.
    score = models.IntegerField(validators=[MinValueValidator(1),
                                            MaxValueValidator(10)])
    # На одно произведение пользователь может оставить только один отзыв!
    title_id = models.ForeignKey(
        Title, on_delete=models.CASCADE, related_name='review')

    def __str__(self):
        return self.text


class Comment(models.Model):
    """Класс для работы с комментариями на отзывы пользователей."""

    text = models.TextField()
    author_id = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='comment_author')
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)
    review_id = models.ForeignKey(
        Review, on_delete=models.CASCADE, related_name='comment')

    def __str__(self):
        return self.text
