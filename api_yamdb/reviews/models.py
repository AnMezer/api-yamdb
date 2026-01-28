from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models

from constants.constants import USERS_ROLES


class User(AbstractUser):
    email = models.EmailField(unique=True)
    bio = models.TextField('Биография', blank=True)
    role = models.CharField(
        'Роль',
        choices=USERS_ROLES,
        default=USERS_ROLES[0],
        blank=True)

    def clean_username(self):
        username = self.cleaned_data.get('username')

        if username.lower == 'me':
            raise ValidationError('Данное имя пользователя запрещено')

        return username

    def __str__(self):
        return self.username
