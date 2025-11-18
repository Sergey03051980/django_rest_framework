from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from materials.models import Course, Lesson, Subscription
from users.models import User


class CourseTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@test.com',
            password='testpass123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        self.course = Course.objects.create(
            title='Test Course',
            description='Test Description',
            owner=self.user
        )

    def test_course_create(self):
        """Тестирование создания курса"""
        data = {
            'title': 'New Course',
            'description': 'New Description'
        }
        response = self.client.post(
            reverse('course-list'),
            data
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )
        self.assertEqual(Course.objects.count(), 2)

    def test_course_list(self):
        """Тестирование получения списка курсов"""
        response = self.client.get(reverse('course-list'))
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )
        # Проверяем пагинацию
        self.assertIn('results', response.data)
        self.assertEqual(len(response.data['results']), 1)

    def test_course_update_by_owner(self):
        """Тестирование обновления курса владельцем"""
        data = {'title': 'Updated Course'}
        response = self.client.patch(
            reverse('course-detail', args=[self.course.id]),
            data
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )
        self.course.refresh_from_db()
        self.assertEqual(self.course.title, 'Updated Course')


class LessonTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@test.com',
            password='testpass123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        self.course = Course.objects.create(
            title='Test Course',
            owner=self.user
        )

        self.lesson = Lesson.objects.create(
            title='Test Lesson',
            course=self.course,
            owner=self.user
        )

    def test_lesson_create(self):
        """Тестирование создания урока"""
        data = {
            'title': 'New Lesson',
            'course': self.course.id
        }
        response = self.client.post(
            reverse('lesson-list-create'),
            data
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

    def test_lesson_list(self):
        """Тестирование получения списка уроков"""
        response = self.client.get(reverse('lesson-list-create'))
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )


class SubscriptionTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@test.com',
            password='testpass123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        self.course = Course.objects.create(
            title='Test Course',
            owner=self.user
        )

    def test_subscription_create(self):
        """Тестирование создания подписки"""
        response = self.client.post(
            reverse('subscription'),
            {'course_id': self.course.id}
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )
        self.assertTrue(
            Subscription.objects.filter(
                user=self.user,
                course=self.course
            ).exists()
        )

    def test_subscription_delete(self):
        """Тестирование удаления подписки"""
        Subscription.objects.create(user=self.user, course=self.course)
        response = self.client.post(
            reverse('subscription'),
            {'course_id': self.course.id}
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )
        self.assertFalse(
            Subscription.objects.filter(
                user=self.user,
                course=self.course
            ).exists()
        )

        class ValidatorsTestCase(APITestCase):
            def setUp(self):
                self.user = User.objects.create_user(
                    email='test@test.com',
                    password='testpass123'
                )
                self.client = APIClient()
                self.client.force_authenticate(user=self.user)

                self.course = Course.objects.create(
                    title='Test Course',
                    owner=self.user
                )

            def test_youtube_validator_success(self):
                """Тестирование валидатора YouTube ссылок (успех)"""
                valid_urls = [
                    'https://www.youtube.com/watch?v=abc123',
                    'https://youtu.be/abc123',
                    'http://youtube.com/watch?v=abc123'
                ]

                for url in valid_urls:
                    with self.subTest(url=url):
                        try:
                            validate_youtube_only(url)
                        except serializers.ValidationError:
                            self.fail(f"Valid URL {url} failed validation")

            def test_youtube_validator_failure(self):
                """Тестирование валидатора YouTube ссылок (неудача)"""
                invalid_urls = [
                    'https://vimeo.com/123456',
                    'https://rutube.ru/video/abc123/',
                    'https://example.com/video'
                ]

                for url in invalid_urls:
                    with self.subTest(url=url):
                        with self.assertRaises(serializers.ValidationError):
                            validate_youtube_only(url)

            def test_title_length_validator(self):
                """Тестирование валидатора длины названия"""
                # Слишком короткое название
                with self.assertRaises(serializers.ValidationError):
                    validate_title_length('ab')

                # Слишком длинное название
                with self.assertRaises(serializers.ValidationError):
                    validate_title_length('a' * 201)

                # Корректное название
                try:
                    validate_title_length('Valid Title')
                except serializers.ValidationError:
                    self.fail("Valid title failed validation")
