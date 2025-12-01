from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, ignore_result=True)
def send_course_update_notification(self, course_id, course_title):
    """Асинхронная отправка уведомлений об обновлении курса"""
    try:
        from materials.models import Subscription

        print(f"\n{'=' * 60}")
        print(f"🎯 CELERY TASK STARTED")
        print(f"   Course: '{course_title}'")
        print(f"   ID: {course_id}")
        print(f"   Task ID: {self.request.id}")
        print(f"{'=' * 60}")

        # Находим подписчиков
        subscriptions = Subscription.objects.filter(
            course_id=course_id
        ).select_related('user')

        count = subscriptions.count()
        print(f"📊 Found {count} subscribers")

        if count == 0:
            print(f"ℹ️ No subscribers for course {course_title}")
            logger.info(f"No subscribers for course {course_title}")
            print(f"{'=' * 60}\n")
            return  # Выходим без возврата значения

        # Собираем email адреса
        recipient_emails = []
        for sub in subscriptions:
            if sub.user and sub.user.email:
                recipient_emails.append(sub.user.email)
                print(f"  - Subscriber: {sub.user.email}")

        if not recipient_emails:
            print(f"⚠️ No valid emails for course {course_title}")
            logger.warning(f"No valid emails for course {course_title}")
            print(f"{'=' * 60}\n")
            return

        subject = f"🔔 Обновление курса: {course_title}"
        message = f"""Здравствуйте!

Курс "{course_title}", на который вы подписаны, был обновлен.

Зайдите в личный кабинет, чтобы ознакомиться с новыми материалами!

С уважением,
Команда LMS-платформы"""

        # Для тестирования выводим в консоль
        print(f"📧 Would send notifications to: {recipient_emails}")

        # В реальном проекте раскомментируйте:
        # send_mail(
        #     subject=subject,
        #     message=message,
        #     from_email=settings.DEFAULT_FROM_EMAIL,
        #     recipient_list=recipient_emails,
        #     fail_silently=False,
        # )

        print(f"✅ Would send to {len(recipient_emails)} subscribers")
        logger.info(f"Notification ready for {len(recipient_emails)} subscribers")
        print(f"{'=' * 60}\n")

        # НЕ возвращаем значение - ignore_result=True

    except Exception as e:
        print(f"\n{'=' * 60}")
        print(f"❌ CELERY TASK ERROR")
        print(f"   Error: {str(e)}")
        print(f"{'=' * 60}\n")
        logger.error(f"Error sending notifications: {e}")
        # НЕ возвращаем ошибку - просто логируем


@shared_task(bind=True, ignore_result=True)
def check_inactive_users(self):
    """Блокировка пользователей, которые не заходили более месяца"""
    try:
        from .models import User

        print(f"\n{'=' * 60}")
        print(f"🔍 CELERY TASK: check_inactive_users")
        print(f"   Task ID: {self.request.id}")
        print(f"{'=' * 60}")

        thirty_days_ago = timezone.now() - timedelta(days=30)
        print(f"📅 Checking users inactive since: {thirty_days_ago}")

        # Находим активных пользователей, которые не заходили более 30 дней
        inactive_users = User.objects.filter(
            is_active=True,
            last_login__lt=thirty_days_ago
        )

        user_count = inactive_users.count()
        print(f"📊 Found {user_count} inactive users")

        if user_count > 0:
            # Получаем email для отчета
            user_emails = list(inactive_users.values_list('email', flat=True))

            # Блокируем пользователей
            inactive_users.update(is_active=False)

            print(f"🔒 Blocked {user_count} users: {user_emails}")
            logger.info(f"Blocked {user_count} inactive users")
        else:
            print("✅ No inactive users found")
            logger.info("No inactive users found")

        print(f"{'=' * 60}\n")

        # НЕ возвращаем значение - ignore_result=True

    except Exception as e:
        print(f"\n{'=' * 60}")
        print(f"❌ CELERY TASK ERROR: check_inactive_users")
        print(f"   Error: {str(e)}")
        print(f"{'=' * 60}\n")
        logger.error(f"Error checking inactive users: {e}")
        # НЕ возвращаем ошибку - просто логируем
