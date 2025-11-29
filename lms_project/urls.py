from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

# ДОБАВИМ ПРОСТЫЕ VIEWS ДЛЯ STRIPE
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def stripe_success(request):
    return render(request, 'payments/success.html')


@csrf_exempt
def stripe_cancel(request):
    return render(request, 'payments/cancel.html')


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('materials.urls')),
    path('api/', include('users.urls')),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    # ДОБАВИМ ПУБЛИЧНЫЕ URL ДЛЯ STRIPE
    path('stripe/success/', stripe_success, name='stripe-success'),
    path('stripe/cancel/', stripe_cancel, name='stripe-cancel'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
