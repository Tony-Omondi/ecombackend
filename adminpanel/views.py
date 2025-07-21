from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from django.db.models import Sum, Count
from accounts.models import CustomUser, ShippingAddress
from products.models import Category, Product, ProductImage, Variant
from orders.models import Cart, CartItem, Order, OrderItem, Payment, Coupon
from products.serializers import CategorySerializer, ProductSerializer, ProductImageSerializer, VariantSerializer
from orders.serializers import CartSerializer, CartItemSerializer, OrderSerializer, OrderItemSerializer, PaymentSerializer, CouponSerializer
from .serializers import AdminUserSerializer, AdminShippingAddressSerializer, AdminAnalyticsSerializer

class AdminUserListCreateView(generics.ListCreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = AdminUserSerializer
    permission_classes = [IsAdminUser]

class AdminUserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = AdminUserSerializer
    permission_classes = [IsAdminUser]

class AdminShippingAddressListCreateView(generics.ListCreateAPIView):
    queryset = ShippingAddress.objects.all()
    serializer_class = AdminShippingAddressSerializer
    permission_classes = [IsAdminUser]

class AdminShippingAddressDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ShippingAddress.objects.all()
    serializer_class = AdminShippingAddressSerializer
    permission_classes = [IsAdminUser]

class AdminCategoryListCreateView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminUser]

class AdminCategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminUser]

class AdminProductListCreateView(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAdminUser]

class AdminProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAdminUser]

class AdminProductImageListCreateView(generics.ListCreateAPIView):
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer
    permission_classes = [IsAdminUser]

class AdminProductImageDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer
    permission_classes = [IsAdminUser]

class AdminVariantListCreateView(generics.ListCreateAPIView):
    queryset = Variant.objects.all()
    serializer_class = VariantSerializer
    permission_classes = [IsAdminUser]

class AdminVariantDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Variant.objects.all()
    serializer_class = VariantSerializer
    permission_classes = [IsAdminUser]

class AdminCartListView(generics.ListAPIView):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes = [IsAdminUser]

class AdminCartDetailView(generics.RetrieveAPIView):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes = [IsAdminUser]

class AdminOrderListCreateView(generics.ListCreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAdminUser]

class AdminOrderDetailView(generics.RetrieveUpdateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAdminUser]

class AdminOrderItemListView(generics.ListAPIView):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
    permission_classes = [IsAdminUser]

class AdminPaymentListView(generics.ListAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAdminUser]

class AdminCouponListCreateView(generics.ListCreateAPIView):
    queryset = Coupon.objects.all()
    serializer_class = CouponSerializer
    permission_classes = [IsAdminUser]

class AdminCouponDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Coupon.objects.all()
    serializer_class = CouponSerializer
    permission_classes = [IsAdminUser]

class AdminAnalyticsView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        total_sales = Order.objects.filter(payment_status='Paid').aggregate(total=Sum('total_amount'))['total'] or 0
        total_orders = Order.objects.count()
        total_users = CustomUser.objects.count()
        recent_orders = Order.objects.order_by('-created_at')[:5]
        top_products = Product.objects.annotate(
            order_count=Count('orderitem__order'),
            total_sold=Sum('orderitem__product_price')
        ).order_by('-order_count')[:5]

        data = {
            'total_sales': total_sales,
            'total_orders': total_orders,
            'total_users': total_users,
            'recent_orders': OrderSerializer(recent_orders, many=True).data,
            'top_products': ProductSerializer(top_products, many=True).data,
        }
        serializer = AdminAnalyticsSerializer(data)
        return Response(serializer.data)