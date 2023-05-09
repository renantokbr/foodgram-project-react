from rest_framework import exceptions
from django.contrib.auth import password_validation

BANNED_USERNAMES = (
    'me', 'set_password',
)

validate_password = password_validation.validate_password


def validate_username(value):
    value = value.lower()
    if value in BANNED_USERNAMES:
        raise exceptions.ValidationError('Некорректное имя пользователя.')
    return value
