from rest_framework import serializers
from .models import Payment, User
from materials.validators import validate_phone_number


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'
        read_only_fields = ('user', 'payment_date')


class UserPaymentSerializer(serializers.ModelSerializer):
    payments = PaymentSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ('id', 'email', 'phone', 'city', 'avatar', 'payments')

    # Добавляем валидатор для телефона
    phone = serializers.CharField(
        validators=[validate_phone_number],
        required=False,
        allow_blank=True
    )
