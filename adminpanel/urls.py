from django.urls import path
from . import views

app_name = 'adminpanel'

urlpatterns = [
    path('users/', views.AdminUserListCreateView.as_view(), name='user_list_create'),
    path('users/<int:pk>/', views.AdminUserDetailView.as_view(), name='user_detail'),
    path('shipping-addresses/', views.AdminShippingAddressListCreateView.as_view(), name='shipping_address_list_create'),
    path('shipping-addresses/<int:pk>/', views.AdminShippingAddressDetailView.as_view(), name='shipping_address_detail'),
    path('categories/', views.AdminCategoryListCreateView.as_view(), name='category_list_create'),
    path('categories/<int:pk>/', views.AdminCategoryDetailView.as_view(), name='category_detail'),
    path('products/', views.AdminProductListCreateView.as_view(), name='product_list_create'),
    path('products/<int:pk>/', views.AdminProductDetailView.as_view(), name='product_detail'),
    path('product-images/', views.AdminProductImageListCreateView.as_view(), name='product_image_list_create'),
    path('product-images/<int:pk>/', views.AdminProductImageDetailView.as_view(), name='product_image_detail'),
    path('variants/', views.AdminVariantListCreateView.as_view(), name='variant_list_create'),
    path('variants/<int:pk>/', views.AdminVariantDetailView.as_view(), name='variant_detail'),
    path('carts/', views.AdminCartListView.as_view(), name='cart_list'),
    path('carts/<int:pk>/', views.AdminCartDetailView.as_view(), name='cart_detail'),
    path('orders/', views.AdminOrderListCreateView.as_view(), name='order_list_create'),
    path('orders/<int:pk>/', views.AdminOrderDetailView.as_view(), name='order_detail'),
    path('order-items/', views.AdminOrderItemListView.as_view(), name='order_item_list'),
    path('payments/', views.AdminPaymentListView.as_view(), name='payment_list'),
    path('coupons/', views.AdminCouponListCreateView.as_view(), name='coupon_list_create'),
    path('coupons/<int:pk>/', views.AdminCouponDetailView.as_view(), name='coupon_detail'),
    path('analytics/', views.AdminAnalyticsView.as_view(), name='analytics'),
]