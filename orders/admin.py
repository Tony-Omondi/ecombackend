from django.contrib import admin
from .models import Cart, CartItem, Order, OrderItem, Payment, Coupon

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['uid', 'user', 'is_paid', 'coupon']
    search_fields = ['user__email', 'uid']

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['cart', 'product', 'variant', 'quantity']
    search_fields = ['cart__user__email', 'product__name']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_id', 'user', 'total_amount', 'status', 'payment_status', 'created_at']
    search_fields = ['user__email', 'order_id']
    list_filter = ['status', 'payment_status']

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'variant', 'quantity', 'product_price']
    search_fields = ['product__name']

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['order', 'amount', 'reference', 'payment_status', 'created_at']
    search_fields = ['order__order_id', 'reference']

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ['coupon_code', 'discount_amount', 'minimum_amount', 'is_expired']
    search_fields = ['coupon_code']