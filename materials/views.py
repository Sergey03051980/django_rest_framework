from rest_framework import viewsets, generics, permissions  # Добавляем viewsets в импорт
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from .models import Course, Lesson, Subscription
from .serializers import CourseSerializer, LessonSerializer
from .paginators import MaterialsPaginator
from users.permissions import IsOwner, IsModerator, IsNotModerator
from rest_framework import status  # Добавляем импорт
from django.utils import timezone
from datetime import timedelta


class SubscriptionAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        course_id = request.data.get('course_id')

        # Конвертируем course_id в int
        try:
            course_id = int(course_id)
        except (TypeError, ValueError):
            return Response(
                {"detail": "course_id must be a number"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            course_item = Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            return Response(
                {"detail": "No Course matches the given query."},
                status=status.HTTP_404_NOT_FOUND
            )

        subs_item = Subscription.objects.filter(user=user, course=course_item)

        # Если подписка есть - удаляем ее
        if subs_item.exists():
            subs_item.delete()
            message = 'Подписка удалена'
        # Если подписки нет - создаем ее
        else:
            Subscription.objects.create(user=user, course=course_item)
            message = 'Подписка добавлена'

        return Response({"message": message})


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = MaterialsPaginator

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
        instance = serializer.save()

        # Дополнительное задание: проверка времени последнего обновления
        four_hours_ago = timezone.now() - timedelta(hours=4)

        # Если курс не обновлялся более 4 часов, отправляем уведомления
        if instance.updated_at and instance.updated_at < four_hours_ago:
            # Запускаем асинхронную задачу
            send_course_update_notification.delay(
                course_id=instance.id,
                course_title=instance.title
            )

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


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

class SubscriptionAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        return None
