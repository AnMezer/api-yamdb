from django.db import models

from constants.constants import CHAR_FIELD_LENGTH, SLUG_FIELD_LENGTH


class NameSlugBaseModel(models.Model):
    name = models.CharField('Название', max_length=CHAR_FIELD_LENGTH)
    slug = models.SlugField(
        max_length=SLUG_FIELD_LENGTH,
        unique=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name
