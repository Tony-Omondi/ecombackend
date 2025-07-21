from rest_framework import serializers
from accounts.models import CustomUser, ShippingAddress
from products.models import Category, Product, ProductImage, Variant
from orders.models import Cart, CartItem, Order, OrderItem, Payment, Coupon
from products.serializers import CategorySerializer, ProductSerializer, ProductImageSerializer, VariantSerializer
from orders.serializers import CartSerializer, CartItemSerializer, OrderSerializer, OrderItemSerializer, PaymentSerializer, CouponSerializer

class AdminUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'first_name', 'last_name', 'is_active', 'is_staff', 'is_superuser', 'date_joined']

class AdminShippingAddressSerializer(serializers.ModelSerializer):
    user = AdminUserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.all(), source='user', write_only=True
    )

    class Meta:
        model = ShippingAddress
        fields = ['id', 'user', 'user_id', 'address', 'city', 'postal_code', 'country', 'current_address', 'created_at', 'updated_at']

class AdminAnalyticsSerializer(serializers.Serializer):
    total_sales = serializers.FloatField()
    total_orders = serializers.IntegerField()
    total_users = serializers.IntegerField()
    recent_orders = OrderSerializer(many=True)
    top_products = ProductSerializer(many=True)