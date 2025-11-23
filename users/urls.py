from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PaymentViewSet, UserViewSet
from .views import payment_success, payment_cancel
from .views import PaymentViewSet, UserViewSet, payment_success, payment_cancel

router = DefaultRouter()
router.register(r'payments', PaymentViewSet, basename='payment')
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),
    path('payments/success/', payment_success, name='payment-success'),
    path('payments/cancel/', payment_cancel, name='payment-cancel'),
]
