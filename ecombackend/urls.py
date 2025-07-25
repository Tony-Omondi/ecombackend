from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/accounts/', include('accounts.urls')),  # Include accounts app URLs
    path('api/auth/', include('dj_rest_auth.urls')),
    path('api/auth/social/', include('social_django.urls', namespace='social')),
    path('api/products/', include('products.urls')),  # Add products app
    path('api/orders/', include('orders.urls')),  # Add products app
    path('api/adminpanel/', include('adminpanel.urls')),
    path('api/notifications/', include('notifications.urls')),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)