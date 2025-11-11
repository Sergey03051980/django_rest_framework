from rest_framework import viewsets, generics, permissions
from django_filters.rest_framework import DjangoFilterBackend
from .models import Course, Lesson
from .serializers import CourseSerializer, LessonSerializer
from users.permissions import IsOwner, IsModerator, IsNotModerator


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        """Разные права для разных действий"""
        if self.action == 'create':
            self.permission_classes = [IsNotModerator]
        elif self.action in ['update', 'partial_update', 'destroy']:
            self.permission_classes = [IsOwner | IsModerator]
        return super().get_permissions()

    def perform_create(self, serializer):
        """Автоматически назначаем владельца при создании"""
        serializer.save(owner=self.request.user)


class LessonListCreateAPIView(generics.ListCreateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [permissions.IsAuthenticated]

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
    