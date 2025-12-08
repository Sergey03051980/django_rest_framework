from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
import logging

class Course(models.Model):
    title = models.CharField(max_length=200, verbose_name='Название')
    preview = models.ImageField(upload_to='courses/previews/', blank=True, null=True, verbose_name='Превью')
    description = models.TextField(blank=True, null=True, verbose_name='Описание')
    owner = models.ForeignKey('users.User', on_delete=models.CASCADE, null=True, blank=True, verbose_name='Владелец')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    class Meta:
        verbose_name = 'Курс'
        verbose_name_plural = 'Курсы'
        ordering = ['id']

    def __str__(self):
        return self.title


class Lesson(models.Model):
    title = models.CharField(max_length=200, verbose_name='Название')
    description = models.TextField(blank=True, null=True, verbose_name='Описание')
    preview = models.ImageField(upload_to='lessons/previews/', blank=True, null=True, verbose_name='Превью')
    video_link = models.URLField(blank=True, null=True, verbose_name='Ссылка на видео')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons', verbose_name='Курс')
    owner = models.ForeignKey('users.User', on_delete=models.CASCADE, null=True, blank=True, verbose_name='Владелец')

    class Meta:
        verbose_name = 'Урок'
        verbose_name_plural = 'Уроки'
        ordering = ['id']

    def __str__(self):
        return self.title


# ТОЛЬКО ОДИН КЛАСС Subscription!
class Subscription(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, verbose_name='Пользователь')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, verbose_name='Курс')
    is_active = models.BooleanField(default=True, verbose_name='Активна')
    subscribed_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата подписки')

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        unique_together = ['user', 'course']  # Одна подписка на курс для пользователя

    def __str__(self):
        return f"{self.user.email} подписан на {self.course.title}"


logger = logging.getLogger(__name__)


@receiver(post_save, sender=Course)
def course_updated_handler(sender, instance, created, **kwargs):
    """
    Обработчик обновления курса - отправляет уведомления подписчикам.
    Вызывается каждый раз при сохранении модели Course.
    """
    if not created:  # Только при ОБНОВЛЕНИИ, не при создании
        print("\n" + "=" * 70)
        print("🎯 СИГНАЛ СРАБОТАЛ: КУРС ОБНОВЛЕН!")
        print("=" * 70)
        print(f"📝 Название курса: {instance.title}")
        print(f"🔢 ID курса: {instance.id}")
        print(f"⏰ Время обновления: {instance.updated_at}")

        # Всегда отправляем задачу в Celery для теста
        try:
            from users.tasks import send_course_update_notification
            task = send_course_update_notification.delay(instance.id, instance.title)
            print(f"\n✅ ЗАДАЧА ОТПРАВЛЕНА В CELERY")
            print(f"   🆔 ID задачи: {task.id}")
            print(f"   📤 Для курса: '{instance.title}' (ID: {instance.id})")
        except Exception as e:
            print(f"\n❌ ОШИБКА при отправке задачи: {e}")

        print("=" * 70 + "\n")
