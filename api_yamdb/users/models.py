from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models

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
