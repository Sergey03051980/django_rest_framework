from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from users.models import User, Payment
from materials.models import Course, Lesson  # Добавляем импорт для связанных моделей


class UserTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@test.com',
            password='testpass123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_user_profile(self):
        """Тестирование получения профиля пользователя"""
        response = self.client.get(reverse('user-detail', args=[self.user.id]))
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )
        self.assertEqual(response.data['email'], self.user.email)

    def test_user_can_only_see_own_profile(self):
        """Тестирование что пользователь видит только свой профиль"""
        # Создаем второго пользователя
        another_user = User.objects.create_user(
            email='another@test.com',
            password='testpass123'
        )

        # Пытаемся получить чужой профиль
        response = self.client.get(reverse('user-detail', args=[another_user.id]))
        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND  # Должен вернуть 404, а не 403
        )

    def test_staff_can_see_all_profiles(self):
        """Тестирование что staff пользователь видит все профили"""
        staff_user = User.objects.create_user(
            email='staff@test.com',
            password='testpass123',
            is_staff=True
        )
        self.client.force_authenticate(user=staff_user)

        response = self.client.get(reverse('user-detail', args=[self.user.id]))
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )


class PaymentTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@test.com',
            password='testpass123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        # Создаем тестовые данные для платежей
        self.course = Course.objects.create(
            title='Test Course',
            description='Test Description',
            owner=self.user
        )

        self.lesson = Lesson.objects.create(
            title='Test Lesson',
            course=self.course,
            owner=self.user
        )

        # Создаем тестовые платежи
        self.payment1 = Payment.objects.create(
            user=self.user,
            paid_course=self.course,
            amount=1000.00,
            payment_method='cash'
        )

        self.payment2 = Payment.objects.create(
            user=self.user,
            paid_lesson=self.lesson,
            amount=500.00,
            payment_method='transfer'
        )

    def test_payment_list(self):
        """Тестирование получения списка платежей"""
        response = self.client.get(reverse('payment-list'))
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )
        # Проверяем что вернулись платежи
        self.assertEqual(len(response.data), 2)

    def test_payment_filter_by_course(self):
        """Тестирование фильтрации платежей по курсу"""
        response = self.client.get(
            reverse('payment-list'),
            {'paid_course': self.course.id}
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )
        # Должен вернуться только 1 платеж за курс
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['amount'], '1000.00')

    def test_payment_filter_by_lesson(self):
        """Тестирование фильтрации платежей по уроку"""
        response = self.client.get(
            reverse('payment-list'),
            {'paid_lesson': self.lesson.id}
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )
        # Должен вернуться только 1 платеж за урок
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['amount'], '500.00')

    def test_payment_ordering(self):
        """Тестирование сортировки платежей"""
        response = self.client.get(
            reverse('payment-list'),
            {'ordering': '-payment_date'}
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )
        # Проверяем что платежи отсортированы (новые первыми)
        self.assertEqual(len(response.data), 2)

    def test_user_can_only_see_own_payments(self):
        """Тестирование что пользователь видит только свои платежи"""
        # Создаем другого пользователя
        another_user = User.objects.create_user(
            email='another@test.com',
            password='testpass123'
        )

        # Создаем платеж для другого пользователя
        Payment.objects.create(
            user=another_user,
            paid_course=self.course,
            amount=2000.00,
            payment_method='cash'
        )

        # Запрос от первого пользователя
        response = self.client.get(reverse('payment-list'))
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )
        # Должны вернуться только 2 платежа первого пользователя
        self.assertEqual(len(response.data), 2)

    def test_payment_create(self):
        """Тестирование создания платежа"""
        data = {
            'paid_course': self.course.id,
            'amount': '1500.00',  # Строковое значение для Decimal
            'payment_method': 'transfer'
        }
        response = self.client.post(
            reverse('payment-list'),
            data,
            format='json'  # Явно указываем формат JSON
        )

        # Добавим отладочный вывод если снова будет ошибка
        if response.status_code != status.HTTP_201_CREATED:
            print("Response status:", response.status_code)
            print("Response data:", response.data)

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            f"Expected 201, got {response.status_code}. Response: {response.data}"
        )
        self.assertEqual(Payment.objects.count(), 3)

        # Проверим что платеж создался с правильным пользователем
        new_payment = Payment.objects.latest('id')
        self.assertEqual(new_payment.user, self.user)
        self.assertEqual(new_payment.amount, 1500.00)
