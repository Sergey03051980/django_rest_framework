from rest_framework import viewsets, filters, permissions, status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.response import Response
from django.urls import reverse
from django.shortcuts import render

from .models import Payment, User
from .serializers import PaymentSerializer, UserPaymentSerializer
from .permissions import IsOwner
from .services.stripe_service import StripeService
from materials.models import Course, Lesson

# ДОБАВИМ ИМПОРТЫ ДЛЯ PUBLIC VIEWS
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.none()  # Для документации
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['paid_course', 'paid_lesson', 'payment_method']
    ordering_fields = ['payment_date']

    def get_queryset(self):
        """Пользователь видит только свои платежи"""
        if getattr(self, 'swagger_fake_view', False):
            return Payment.objects.none()  # Для документации
        return Payment.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """Автоматически назначаем текущего пользователя при создании платежа"""
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['post'])
    def create_stripe_payment(self, request):
        """Создание платежа через Stripe"""
        user = request.user
        course_id = request.data.get('course_id')
        lesson_id = request.data.get('lesson_id')

        if not course_id and not lesson_id:
            return Response(
                {"error": "Необходимо указать course_id или lesson_id"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Определяем что оплачивается и сумму
        if course_id:
            try:
                course = Course.objects.get(id=course_id)
                amount = 1000.00  # Примерная цена курса
                name = course.title
                description = course.description
            except Course.DoesNotExist:
                return Response(
                    {"error": "Курс не найден"},
                    status=status.HTTP_404_NOT_FOUND
                )
        else:
            try:
                lesson = Lesson.objects.get(id=lesson_id)
                amount = 500.00  # Примерная цена урока
                name = lesson.title
                description = lesson.description
            except Lesson.DoesNotExist:
                return Response(
                    {"error": "Урок не найден"},
                    status=status.HTTP_404_NOT_FOUND
                )

        try:
            # Создаем продукт в Stripe
            product = StripeService.create_product(name, description)

            # Создаем цену
            price = StripeService.create_price(product.id, amount)

            # ИСПРАВИМ URLы - они должны быть абсолютными
            base_url = "http://127.0.0.1:8000"  # Явно указываем базовый URL
            success_url = f"{base_url}/api/payments/success/"
            cancel_url = f"{base_url}/api/payments/cancel/"

            session = StripeService.create_checkout_session(
                price.id,
                success_url,
                cancel_url
            )

            # Создаем запись о платеже в нашей системе
            payment = Payment.objects.create(
                user=user,
                paid_course=course if course_id else None,
                paid_lesson=lesson if lesson_id else None,
                amount=amount,
                payment_method='stripe',
                stripe_product_id=product.id,
                stripe_price_id=price.id,
                stripe_session_id=session.id,
                stripe_payment_link=session.url,
                payment_status='pending'
            )

            return Response({
                "payment_id": payment.id,
                "payment_link": session.url,
                "status": "pending"
            })

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['get'])
    def check_payment_status(self, request, pk=None):
        """Проверка статуса платежа (дополнительное задание)"""
        payment = self.get_object()

        if payment.payment_method != 'stripe' or not payment.stripe_session_id:
            return Response(
                {"error": "Этот платеж не через Stripe"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            session = StripeService.retrieve_session(payment.stripe_session_id)

            # Обновляем статус платежа
            if session.payment_status == 'paid':
                payment.payment_status = 'paid'
                payment.save()

            return Response({
                "payment_id": payment.id,
                "stripe_status": session.payment_status,
                "our_status": payment.payment_status
            })

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserPaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Пользователь видит только свой профиль"""
        if self.request.user.is_staff:
            return User.objects.all()
        return User.objects.filter(id=self.request.user.id)


# 🔥 УДАЛИМ СТАРЫЕ ФУНКЦИИ И ДОБАВИМ НОВЫЕ КЛАССЫ:

@method_decorator(csrf_exempt, name='dispatch')
class PaymentSuccessView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return render(request, 'payments/success.html')


@method_decorator(csrf_exempt, name='dispatch')
class PaymentCancelView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return render(request, 'payments/cancel.html')
