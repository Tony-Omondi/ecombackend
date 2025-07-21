from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('send/order/<int:order_id>/', views.SendOrderConfirmationView.as_view(), name='send_order_confirmation'),
    path('history/', views.NotificationListView.as_view(), name='notification_list'),
    path('history/<int:pk>/', views.NotificationDetailView.as_view(), name='notification_detail'),
]