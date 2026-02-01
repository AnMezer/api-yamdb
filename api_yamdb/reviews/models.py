from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

from .base_models import NameSlugBaseModel
from constants.constants import (
    CHAR_FIELD_LENGTH,
    FORBIDDEN_USERNAME,
)


class User(AbstractUser):
    class Role(models.TextChoices):
        USER = 'user'
        ADMIN = 'admin'
        MODER = 'moderator'
    email = models.EmailField(unique=True)
    bio = models.TextField('Биография', blank=True)
    role = models.CharField(
        'Роль',
        choices=Role,
        default=Role.USER,
        blank=True,
        max_length=CHAR_FIELD_LENGTH
    )

    def clean_username(self):
        username = self.cleaned_data.get('username')

        if username.lower() == FORBIDDEN_USERNAME:
            raise ValidationError('Данное имя пользователя запрещено')

        return username

    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN or self.is_superuser

    @property
    def is_moder(self):
        return self.role == self.Role.ADMIN or self.role == self.Role.MODER

    def __str__(self):
        return self.username


class Category(NameSlugBaseModel):

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'


class Genre(NameSlugBaseModel):

    class Meta:
        verbose_name = 'жанр'
        verbose_name_plural = 'жанры'


class Title(models.Model):
    name = models.CharField('Название', max_length=CHAR_FIELD_LENGTH)
    year = models.PositiveSmallIntegerField()
    # Заглушка, нужно сделать расчет рейтинга из модели Review
    rating = models.PositiveSmallIntegerField(default=None, null=True)
    description = models.TextField('Описание', blank=True)
    genre = models.ManyToManyField(Genre, related_name='titles')
    category = models.ForeignKey(Category,
                                 on_delete=models.SET_NULL,
                                 related_name='titles',
                                 null=True)

    class Meta:
        verbose_name = 'произведение'
        verbose_name_plural = 'произведения'

    def __str__(self):
        return f'{self.name} ({self.year})'


class Review(models.Model):
    """Класс для работы с отзывами на произведения."""

    text = models.TextField()
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='reviews')
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)
    # Оценка произведению - целое число от 1 до 10.
    score = models.IntegerField(validators=[MinValueValidator(1),
                                            MaxValueValidator(10)])
    # На одно произведение пользователь может оставить только один отзыв.
    title = models.ForeignKey(
        Title, on_delete=models.CASCADE, related_name='reviews')

    class Meta:
        ordering = ('-pub_date', )
        verbose_name = 'отзыв'
        verbose_name_plural = 'отзывы'
        constraints = [
            models.UniqueConstraint(
                fields=('title', 'author', ),
                name='unique review'
            )
        ]

    def __str__(self):
        return self.text


class Comment(models.Model):
    """Класс для работы с комментариями на отзывы пользователей."""

    text = models.TextField()
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='comments')
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)
    review = models.ForeignKey(
        Review, on_delete=models.CASCADE, related_name='comments')

    class Meta:
        ordering = ('-pub_date', )
        verbose_name = 'комментарий'
        verbose_name_plural = 'комментарии'

    def __str__(self):
        return self.text
