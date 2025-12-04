from users.tasks import send_course_update_notification
from rest_framework import viewsets, generics, permissions
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
import logging

from .models import Course, Lesson, Subscription
from .serializers import CourseSerializer, LessonSerializer
from .paginators import MaterialsPaginator
from users.permissions import IsOwner, IsModerator, IsNotModerator
from rest_framework import status
from django.utils import timezone
from datetime import timedelta

logger = logging.getLogger(__name__)


class SubscriptionAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        print("\n" + "=" * 50)
        print("📌 SUBSCRIPTION API CALLED")
        print(f"👤 User: {request.user}")
        print(f"📝 Data: {request.data}")

        user = request.user
        course_id = request.data.get('course_id')

        print(f"🎯 Course ID from request: {course_id}")

        # Конвертируем course_id в int
        try:
            course_id = int(course_id)
        except (TypeError, ValueError):
            print("❌ ERROR: course_id must be a number")
            return Response(
                {"detail": "course_id must be a number"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            course_item = Course.objects.get(id=course_id)
            print(f"✅ Course found: {course_item.title} (ID: {course_item.id})")
        except Course.DoesNotExist:
            print(f"❌ ERROR: Course with ID {course_id} not found")
            return Response(
                {"detail": "No Course matches the given query."},
                status=status.HTTP_404_NOT_FOUND
            )

        subs_item = Subscription.objects.filter(user=user, course=course_item)

        # Если подписка есть - удаляем ее
        if subs_item.exists():
            subs_item.delete()
            message = 'Подписка удалена'
            print(f"🗑️ Subscription removed for user {user.email}")
        # Если подписки нет - создаем ее
        else:
            Subscription.objects.create(user=user, course=course_item)
            message = 'Подписка добавлена'
            print(f"✅ Subscription created for user {user.email}")

        print(f"📤 Response: {message}")
        print("=" * 50 + "\n")
        return Response({"message": message})


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = MaterialsPaginator

    def update(self, request, *args, **kwargs):
        print("\n🔧 UPDATE method called")
        print(f"   User: {request.user}")
        print(f"   Data: {request.data}")
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        print("\n🔧 PARTIAL_UPDATE method called")
        print(f"   User: {request.user}")
        print(f"   Data: {request.data}")
        return super().partial_update(request, *args, **kwargs)

    def get_serializer_context(self):
        """Добавляем request в контекст сериализатора"""
        context = super().get_serializer_context()
        context.update({'request': self.request})
        return context

    def get_permissions(self):
        if self.action == 'create':
            self.permission_classes = [IsNotModerator]
        elif self.action in ['update', 'partial_update', 'destroy']:
            self.permission_classes = [IsOwner | IsModerator]
        return super().get_permissions()

    def perform_update(self, serializer):
        print("\n" + "=" * 50)
        print("🔄 COURSE UPDATE STARTED")

        # Получаем текущий объект до сохранения
        instance = self.get_object()
        print(f"📝 Course before update: {instance.title} (ID: {instance.id})")

        # Получаем время обновления до сохранения
        old_updated_at = instance.updated_at
        print(f"⏰ Updated at before update: {old_updated_at}")

        # Сохраняем изменения
        super().perform_update(serializer)

        # Обновляем объект из БД
        instance.refresh_from_db()
        print(f"✅ Course updated: {instance.title}")
        print(f"⏰ Updated at after update: {instance.updated_at}")

        # Проверяем, было ли обновление более 4 часов назад
        four_hours_ago = timezone.now() - timedelta(hours=4)
        print(f"🕐 Threshold time (4 hours ago): {four_hours_ago}")

        # Проверяем: если предыдущее обновление было РАНЬШЕ чем 4 часа назад
        if old_updated_at and old_updated_at < four_hours_ago:
            print("✅ Course wasn't updated for more than 4 hours. Sending notifications...")
            print(
                f"   Sending task to Celery: send_course_update_notification.delay({instance.id}, '{instance.title}')")

            # Запускаем асинхронную задачу
            send_course_update_notification.delay(instance.id, instance.title)

            print("✅ Task sent to Celery")
        else:
            if old_updated_at:
                print(f"⏰ Course was updated recently (at {old_updated_at}). No notifications.")
            else:
                print("ℹ️ No previous update time found. No notifications.")

        print("=" * 50 + "\n")

    def perform_create(self, serializer):
        print("\n📝 Creating new course...")
        serializer.save(owner=self.request.user)
        print(f"✅ Course created by {self.request.user}")


class LessonListCreateAPIView(generics.ListCreateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = MaterialsPaginator

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsNotModerator()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class LessonRetrieveAPIView(generics.RetrieveAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [permissions.IsAuthenticated]


class LessonUpdateAPIView(generics.UpdateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsOwner | IsModerator]


class LessonDestroyAPIView(generics.DestroyAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsOwner | IsModerator]
