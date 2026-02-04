import random

from django.contrib.auth import get_user_model, tokens
from django.core.cache import cache

User = get_user_model()

class ConfirmationCodeService:
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
# class CustomTokenGenerator(tokens.PasswordResetTokenGenerator):
#     confirmation_code = None

#     def __init__(self, confirmation_code):
#         self.confirmation_code = confirmation_code
#         super().__init__()

#     def _make_hash_value(self, user, timestamp):
#         login_timestamp = (
#             ""
#             if user.last_login is None
#             else user.last_login.replace(microsecond=0, tzinfo=None)
#         )
#         return (
#             f"{user.pk}{user.password}{login_timestamp}"
#             f"{timestamp}{user.email}{self.confirmation_code}"
#         )


# # class CustomTokenGenerator(tokens.default_token_generator):
# #     confirmation_code = None

# #     def __init__(self, confirmation_code):
# #         super().__init__(self)
# #         self.confirmation_code = confirmation_code

# #     def _make_hash_value(self, user, timestamp, confirmation_code):
# #         super()._make_hash_value(user, timestamp)
# #         return (f'{user.pk}{user.password}{login_timestamp}'
# #                 f'{timestamp}{email}{str(confirmation_code)}')

# #customtokengenerator = CustomTokenGenerator(confirmation_code)


# class TokenAndConfirmationCodeService:
#     @staticmethod
#     def generate_token_and_code(user):
#         code = str(random.randint(100000, 999999))
#         customtokentoken = CustomTokenGenerator(code)
#         customtokentoken.make_token(user)
#         # cache_key = f'confirmation_code_{user.email}'
#         # cache.set(cache_key, {
#         #     'code': code,
#         #     'user_id': user.id
#         # }, timeout=300)

#         return code

#     @staticmethod
#     def verify_code(user, code):
#         cache_key = f'confirmation_code_{user.email}'
#         cached_data = cache.get(cache_key)

#         if not cached_data:
#             return None

#         if cached_data['code'] == code:
#             cache.delete(cache_key)
#             return User.objects.get(id=cached_data['user_id'])

#         return None
