from rest_framework import serializers
from .models import Course, Lesson
from .validators import validate_youtube_only, validate_title_length, validate_description_not_empty

class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = '__all__'
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=Lesson.objects.all(),
                fields=['title', 'course'],
                message='Урок с таким названием уже существует в этом курсе'
            )
        ]

    # Добавляем валидаторы к полям
    title = serializers.CharField(validators=[validate_title_length])
    description = serializers.CharField(
        validators=[validate_description_not_empty],
        required=False,
        allow_blank=True
    )
    video_link = serializers.URLField(
        validators=[validate_youtube_only],
        required=False,
        allow_null=True
    )

class CourseSerializer(serializers.ModelSerializer):
    lessons = LessonSerializer(many=True, read_only=True)
    lessons_count = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = '__all__'

    # Добавляем валидаторы
    title = serializers.CharField(validators=[validate_title_length])
    description = serializers.CharField(
        validators=[validate_description_not_empty],
        required=False,
        allow_blank=True
    )

    def get_lessons_count(self, obj):
        return obj.lessons.count()
