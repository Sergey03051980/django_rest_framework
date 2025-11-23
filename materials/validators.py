from rest_framework import serializers
from urllib.parse import urlparse
import re
from datetime import datetime


def validate_youtube_only(value):
    """Валидатор для проверки что ссылка ведет только на youtube.com"""
    if value:
        parsed_url = urlparse(value)
        domain = parsed_url.netloc.lower()

        allowed_domains = ['youtube.com', 'www.youtube.com', 'youtu.be']

        if not any(domain.endswith(allowed) for allowed in allowed_domains):
            raise serializers.ValidationError(
                "Разрешены только ссылки на YouTube. "
                "Пример: https://www.youtube.com/watch?v=..."
            )
    return value


def validate_phone_number(value):
    """Валидатор для номера телефона"""
    if value:
        # Упрощенная проверка телефона
        cleaned_phone = re.sub(r'\D', '', value)
        if len(cleaned_phone) not in [10, 11]:
            raise serializers.ValidationError(
                "Некорректный формат номера телефона. "
                "Пример: +7 999 123-45-67 или 89991234567"
            )
    return value


def validate_title_length(value):
    """Валидатор для длины названия"""
    if len(value) < 3:
        raise serializers.ValidationError(
            "Название должно содержать минимум 3 символа"
        )
    if len(value) > 200:
        raise serializers.ValidationError(
            "Название не должно превышать 200 символов"
        )
    return value


def validate_description_not_empty(value):
    """Валидатор для проверки что описание не пустое"""
    if value and len(value.strip()) < 10:
        raise serializers.ValidationError(
            "Описание должно содержать минимум 10 символов"
        )
    return value
