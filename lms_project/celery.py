import os
from celery import Celery
from celery.schedules import crontab

# Установка настроек Django по умолчанию
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lms_project.settings')

app = Celery('lms_project')

# Чтение настроек из Django settings с префиксом CELERY_
app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматическое обнаружение задач из всех зарегистрированных приложений
app.autodiscover_tasks()

# Настройка периодических задач (Celery Beat)
app.conf.beat_schedule = {
    'check-inactive-users-every-day': {
        'task': 'users.tasks.check_inactive_users',
        'schedule': crontab(hour=0, minute=0),  # Каждый день в полночь
    },
}

app.conf.timezone = 'Europe/Moscow'
