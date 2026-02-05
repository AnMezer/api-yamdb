from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from constants.constants import (
    CHAR_FIELD_LENGTH,
    FORBIDDEN_USERNAME,
    MIN_SCORE,
    MAX_SCORE
)

from .base_models import NameSlugBaseModel, PublicationBaseModel


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


class Review(PublicationBaseModel):
    """Класс для работы с отзывами на произведения."""

    # Оценка произведению - целое число от 1 до 10.
    score = models.PositiveSmallIntegerField(
        'Оценка',
        validators=[MinValueValidator(MIN_SCORE),
                    MaxValueValidator(MAX_SCORE)]
    )
    # На одно произведение пользователь может оставить только один отзыв.
    title = models.ForeignKey(
        'Название произведения',
        Title,
        on_delete=models.CASCADE,
        related_name='reviews'
    )

    class Meta(PublicationBaseModel.Meta):
        verbose_name = 'отзыв'
        verbose_name_plural = 'отзывы'
        constraints = [models.UniqueConstraint(
            fields=('title', 'author'), name='unique review')
        ]


class Comment(PublicationBaseModel):
    """Класс для работы с комментариями на отзывы пользователей."""

    review = models.ForeignKey(
        'Комментарий',
        Review,
        on_delete=models.CASCADE,
        related_name='comments'
    )

    class Meta(PublicationBaseModel.Meta):
        verbose_name = 'комментарий'
        verbose_name_plural = 'комментарии'
