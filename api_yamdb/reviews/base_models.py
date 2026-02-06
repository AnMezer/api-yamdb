from django.contrib.auth import get_user_model
from django.db import models

from constants.constants import CHAR_FIELD_LENGTH, SLUG_FIELD_LENGTH


User = get_user_model()


class NameSlugBaseModel(models.Model):
    name = models.CharField('Название', max_length=CHAR_FIELD_LENGTH)
    slug = models.SlugField(
        max_length=SLUG_FIELD_LENGTH,
        unique=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name


class PublicationBaseModel(models.Model):
    """Базовая абстрактная модель для создания публикаций разного рода."""

    text = models.TextField('Текст')
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='%(class)s_authors',
        verbose_name='Автор')

    class Meta:
        abstract = True
        ordering = ('-pub_date', )

    def __str__(self):
        return self.text
