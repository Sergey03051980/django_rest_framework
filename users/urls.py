from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PaymentViewSet, UserViewSet

router = DefaultRouter()
router.register(r'payments', PaymentViewSet, basename='payment')  # Добавляем basename
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),
]
