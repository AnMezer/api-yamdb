import random

from django.contrib.auth import get_user_model
from django.core.cache import cache

User = get_user_model()


class ConfirmationCodeService:
    """Класс создания и валидации кода подверждения в кэше."""
    @staticmethod
    def generate_code(user):
        code = str(random.randint(100000, 999999))

        cache_key = f'confirmation_code_{user.email}'
        cache.set(cache_key, {
            'code': code,
            'user_id': user.id
        }, timeout=300)

        return code

    @staticmethod
    def verify_code(user, code):
        cache_key = f'confirmation_code_{user.email}'
        cached_data = cache.get(cache_key)

        if not cached_data:
            return None

        if cached_data['code'] == code:
            cache.delete(cache_key)
            return User.objects.get(id=cached_data['user_id'])

        return None
