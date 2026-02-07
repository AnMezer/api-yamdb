from datetime import timedelta

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from constants.constants import (
    CHAR_FIELD_LENGTH,
    FORBIDDEN_USERNAME,
    ATTEMPT
)


class User(AbstractUser):
    """Кастомный класс пользователя."""
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

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN or self.is_superuser

    @property
    def is_moder(self):
        return self.role == self.Role.ADMIN or self.role == self.Role.MODER

    def __str__(self):
        return self.username


class VerifyCode(models.Model):
    """Модель кода потдвержения"""
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='confirmation_code')
    code = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    failed_attempt = models.IntegerField(default=ATTEMPT)
    is_used = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Код доступа'
        verbose_name_plural = 'Коды доступа'

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(
                hours=settings.CONFIRMATION_CODES_EXPAIRED_HOUR_COUNT)
        super().save(*args, **kwargs)

    @property
    def is_valid(self):
        return (not self.is_used and timezone.now() < self.expires_at
                and (self.failed_attempt
                     <= settings.MAX_AUTHORIZATION_ATTEMPTS))

    @property
    def increase_attempts(self):
        self.failed_attempt += 1
        self.save()
