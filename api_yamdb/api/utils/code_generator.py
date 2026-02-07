import random

from django.contrib.auth import get_user_model

from constants.constants import MAX_RANDOM_VALUE, MIN_RANDOM_VALUE

User = get_user_model()


class GeneratingCodeService:
    @staticmethod
    def generate_code():
        code = str(random.randint(MIN_RANDOM_VALUE, MAX_RANDOM_VALUE))
        return code
