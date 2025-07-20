from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('cart/', views.CartListCreateView.as_view(), name='cart_list_create'),
    path('cart/items/', views.CartItemListCreateView.as_view(), name='cart_item_list_create'),
    path('cart/items/<int:pk>/', views.CartItemDetailView.as_view(), name='cart_item_detail'),
    path('cart/apply-coupon/', views.ApplyCouponView.as_view(), name='apply_coupon'),
    path('orders/', views.OrderListCreateView.as_view(), name='order_list_create'),
    path('orders/<int:pk>/', views.OrderDetailView.as_view(), name='order_detail'),
    path('payment/initiate/', views.InitiatePaymentView.as_view(), name='initiate_payment'),
    path('payment/callback/', views.PaymentCallbackView.as_view(), name='payment_callback'),
]