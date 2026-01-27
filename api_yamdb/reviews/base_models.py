from django.db import models
from django.core.validators import RegexValidator
#from django.utils.text import slugify

from constants.constants import (CHAR_FIELD_LENGTH, SLUG_FIELD_LENGTH,
                                 REGEX_STAMP)


class NameSlugBaseModel(models.Model):
    name = models.CharField('Название', max_length=CHAR_FIELD_LENGTH)
    slug = models.SlugField(
        max_length=SLUG_FIELD_LENGTH,
        unique=True,
        validators=[
            RegexValidator(
                regex=REGEX_STAMP,
                message=f'slug может содержать символы: {REGEX_STAMP}',
                code='invalid_slug')])

    #def save(self, *args, **kwargs):
    #    "Генерируем слаг из имени, если не заполнен"
    #    if not self.slug:
    #        self.slug = slugify(self.name)
    #    super().save(*args, **kwargs)

    class Meta:
        abstract = True
