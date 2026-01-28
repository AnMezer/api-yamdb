from django.contrib.auth.models import AbstractUser
from django.db import models

from constants.constants import USERS_ROLES, CHAR_FIELD_LENGTH
from .base_models import NameSlugBaseModel


class User(AbstractUser):
    pass
    # bio = models.TextField()
    # role = models.Choices(s)


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
    genre = models.ManyToManyField(Genre, related_name='titles')
    category = models.ForeignKey(Category,
                                 on_delete=models.SET_NULL,
                                 related_name='titles',
                                 null=True)

    class Meta:
        verbose_name = 'произведение'
        verbose_name_plural = 'произведения'
