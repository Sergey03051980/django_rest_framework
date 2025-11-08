from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Payment, User
from .serializers import PaymentSerializer, UserPaymentSerializer


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['paid_course', 'paid_lesson', 'payment_method']
    ordering_fields = ['payment_date']


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserPaymentSerializer


from django.shortcuts import render

# Create your views here.
