from django.conf import settings

FIRST_API_VERSION = 'v1'
USERS_ROLES = {
    settings.USER_ROLE: 'user',
    settings.MODERATOR_ROLE: 'moderator',
    settings.ADMIN_ROLE: 'admin'
}
CHAR_FIELD_LENGTH = 256
SLUG_FIELD_LENGTH = 50
REGEX_STAMP = '^[-a-zA-Z0-9_]+$'
FORBIDDEN_USERNAME = 'me'

