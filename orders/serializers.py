from rest_framework import serializers
from .models import Cart, CartItem, Order, OrderItem, Payment, Coupon
from products.models import Product, Variant
from accounts.models import ShippingAddress
from products.serializers import ProductSerializer, VariantSerializer

class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = ['id', 'coupon_code', 'discount_amount', 'minimum_amount', 'is_expired']

class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), source='product', write_only=True
    )
    variant = VariantSerializer(read_only=True)
    variant_id = serializers.PrimaryKeyRelatedField(
        queryset=Variant.objects.all(), source='variant', write_only=True, required=False
    )

    class Meta:
        model = CartItem
        fields = ['id', 'cart', 'product', 'product_id', 'variant', 'variant_id', 'quantity', 'created_at', 'updated_at']

    def validate(self, data):
        if data.get('variant') and data['variant'].product != data['product']:
            raise serializers.ValidationError("Variant must belong to the selected product.")
        return data

class CartSerializer(serializers.ModelSerializer):
    cart_items = CartItemSerializer(many=True, read_only=True)
    coupon = CouponSerializer(read_only=True)
    coupon_code = serializers.CharField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = Cart
        fields = ['id', 'user', 'is_paid', 'coupon', 'coupon_code', 'cart_items', 'created_at', 'updated_at']

    def validate_coupon_code(self, value):
        if not value:
            return None
        try:
            coupon = Coupon.objects.get(coupon_code__iexact=value)
            if coupon.is_expired:
                raise serializers.ValidationError("Coupon has expired.")
            if self.instance and self.instance.get_cart_total() < coupon.minimum_amount:
                raise serializers.ValidationError(
                    f"Minimum order amount for this coupon is KSh {coupon.minimum_amount}"
                )
            return coupon
        except Coupon.DoesNotExist:
            raise serializers.ValidationError("Invalid coupon code.")

class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), source='product', write_only=True
    )
    variant = VariantSerializer(read_only=True)
    variant_id = serializers.PrimaryKeyRelatedField(
        queryset=Variant.objects.all(), source='variant', write_only=True, required=False
    )

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_id', 'variant', 'variant_id', 'quantity', 'product_price']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=False)
    shipping_address = serializers.PrimaryKeyRelatedField(
        queryset=ShippingAddress.objects.all()
    )
    coupon = CouponSerializer(read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'user', 'order_id', 'shipping_address', 'total_amount', 'coupon', 'payment_status', 'payment_mode', 'status', 'items', 'created_at', 'updated_at']

    def validate(self, data):
        user = self.context['request'].user
        if data['shipping_address'].user != user:
            raise serializers.ValidationError("Shipping address must belong to the user.")
        return data

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        order = Order.objects.create(**validated_data)
        total_amount = 0
        for item_data in items_data:
            price = item_data['product'].price if not item_data.get('variant') else item_data['product'].price
            total_amount += price * item_data['quantity']
            OrderItem.objects.create(order=order, product_price=price, **item_data)
        order.total_amount = total_amount
        if order.coupon and not order.coupon.is_expired:
            order.total_amount = max(total_amount - order.coupon.discount_amount, 0)
        order.save()
        return order

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'order', 'amount', 'reference', 'payment_status', 'created_at']