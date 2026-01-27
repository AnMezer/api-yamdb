from django.contrib.auth.models import AbstractUser
from django.db import models

from constants.constants import USERS_ROLES


class User(AbstractUser):
    pass
    # bio = models.TextField()
    # role = models.Choices(s)
