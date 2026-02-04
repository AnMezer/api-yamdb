from datetime import datetime
from django.core.exceptions import ValidationError


def validate_current_year(value):
    """Проверка, что год не больше текущего."""
    if value > datetime.now().year:
        raise ValidationError('Год не может быть больше текущего')
