from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models

from .base_models import NameSlugBaseModel
from constants.constants import (
    CHAR_FIELD_LENGTH,
    FORBIDDEN_USERNAME,
    USERS_ROLES
)


class User(AbstractUser):
    email = models.EmailField(unique=True)
    bio = models.TextField('Биография', blank=True)
    role = models.IntegerField(
        'Роль',
        choices=USERS_ROLES,
        default=USERS_ROLES[0][0],
        blank=True
    )

    def clean_username(self):
        username = self.cleaned_data.get('username')

        if username.lower == FORBIDDEN_USERNAME:
            raise ValidationError('Данное имя пользователя запрещено')

        return username

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
    rating = models.PositiveSmallIntegerField(default=1)  # Заглушка, нужно сделать расчет рейтинга из модели Review
    description = models.TextField('Описание', blank=True)
    genre = models.ManyToManyField(Genre, related_name='title_genres')
    category = models.ManyToManyField(Category, related_name='title_categories')

    class Meta:
        verbose_name = 'произведение'
        verbose_name_plural = 'произведения'
