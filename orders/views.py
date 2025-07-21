from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Cart, CartItem, Order, Payment, Coupon
from .serializers import CartSerializer, CartItemSerializer, OrderSerializer, PaymentSerializer
from products.models import Product, Variant
import requests
from django.conf import settings
from django.core.mail import send_mail
from notifications.models import Notification

class CartListCreateView(generics.ListCreateAPIView):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user, is_paid=False)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class CartItemListCreateView(generics.ListCreateAPIView):
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return CartItem.objects.filter(cart__user=self.request.user, cart__is_paid=False)

    def perform_create(self, serializer):
        product = serializer.validated_data['product']
        variant = serializer.validated_data.get('variant')
        quantity = serializer.validated_data['quantity']
        cart, _ = Cart.objects.get_or_create(user=self.request.user, is_paid=False)
        available_stock = variant.stock if variant else product.stock
        if quantity > available_stock:
            raise serializers.ValidationError("Insufficient stock.")
        serializer.save(cart=cart)

class CartItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return CartItem.objects.filter(cart__user=self.request.user, cart__is_paid=False)

class ApplyCouponView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        cart = Cart.objects.filter(user=request.user, is_paid=False).first()
        if not cart:
            return Response({"error": "No active cart found."}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = CartSerializer(cart, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class OrderListCreateView(generics.ListCreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Order.objects.all()
        return Order.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        cart = Cart.objects.filter(user=self.request.user, is_paid=False).first()
        if not cart or not cart.cart_items.exists():
            raise serializers.ValidationError("Cart is empty.")
        serializer.save(
            user=self.request.user,
            coupon=cart.coupon,
            items=[
                {
                    'product': item.product,
                    'variant': item.variant,
                    'quantity': item.quantity
                } for item in cart.cart_items.all()
            ]
        )

class OrderDetailView(generics.RetrieveUpdateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Order.objects.all()
        return Order.objects.filter(user=self.request.user)

class InitiatePaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        cart = Cart.objects.filter(user=self.request.user, is_paid=False).first()
        if not cart or not cart.cart_items.exists():
            return Response({"status": False, "message": "Your cart is empty"}, status=status.HTTP_400_BAD_REQUEST)

        amount = int(cart.get_cart_total_price_after_coupon() * 100)
        email = self.request.user.email
        callback_url = request.build_absolute_uri('/api/orders/payment/callback/')

        headers = {
            "Authorization": f"Bearer {settings.PAYSTACK_TEST_SECRET_KEY}",
            "Content-Type": "application/json",
        }

        data = {
            "email": email,
            "amount": amount,
            "callback_url": callback_url,
            "metadata": {
                "cart_id": str(cart.uid),
                "custom_fields": [
                    {
                        "display_name": "Cart Items",
                        "variable_name": "cart_items",
                        "value": ", ".join([item.product.name for item in cart.cart_items.all()])
                    }
                ]
            }
        }

        try:
            response = requests.post(settings.PAYSTACK_INITIALIZE_URL, headers=headers, json=data)
            if response.status_code == 200:
                response_data = response.json()
                return Response({
                    'status': True,
                    'authorization_url': response_data['data']['authorization_url'],
                    'reference': response_data['data']['reference']
                })
            return Response({
                'status': False,
                'message': "Payment initialization failed"
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'status': False,
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class PaymentCallbackView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        reference = request.query_params.get('reference')
        if not reference:
            return Response({"status": False, "message": "Payment verification failed"}, status=status.HTTP_400_BAD_REQUEST)

        headers = {
            "Authorization": f"Bearer {settings.PAYSTACK_TEST_SECRET_KEY}",
            "Content-Type": "application/json",
        }

        try:
            response = requests.get(f"{settings.PAYSTACK_VERIFY_URL}{reference}", headers=headers)
            if response.status_code == 200:
                response_data = response.json()
                if response_data['status'] and response_data['data']['status'] == 'success':
                    cart_id = response_data['data']['metadata']['cart_id']
                    cart = Cart.objects.get(uid=cart_id, user=self.request.user)
                    cart.is_paid = True
                    cart.save()

                    # Create order and reduce stock
                    order = Order.objects.create(
                        user=self.request.user,
                        order_id=reference,
                        shipping_address=cart.user.shippingaddress_set.filter(current_address=True).first(),
                        total_amount=cart.get_cart_total_price_after_coupon(),
                        coupon=cart.coupon,
                        payment_status="Paid",
                        payment_mode="Paystack",
                        status="confirmed"
                    )
                    for item in cart.cart_items.all():
                        price = item.product.price
                        OrderItem.objects.create(
                            order=order,
                            product=item.product,
                            variant=item.variant,
                            quantity=item.quantity,
                            product_price=price
                        )
                        # Reduce stock
                        if item.variant:
                            item.variant.stock -= item.quantity
                            item.variant.save()
                        else:
                            item.product.stock -= item.quantity
                            item.product.save()

                    payment = Payment.objects.create(
                        order=order,
                        amount=order.total_amount,
                        reference=reference,
                        payment_status="completed"
                    )
                    cart.cart_items.all().delete()  # Clear cart

                    # Send order confirmation email
                    items = OrderItem.objects.filter(order=order)
                    item_list = "\n".join([f"- {item.product.name} (Qty: {item.quantity}, Price: KSh {item.product_price:.2f})" for item in items])
                    subject = f"Order Confirmation: {order.order_id}"
                    message = (
                        f"Dear {order.user.first_name or order.user.email},\n\n"
                        f"Thank you for your order!\n\n"
                        f"Order ID: {order.order_id}\n"
                        f"Total Amount: KSh {order.total_amount:.2f}\n"
                        f"Status: {order.status}\n"
                        f"Payment Status: {order.payment_status}\n"
                        f"Shipping Address: {order.shipping_address.address}, {order.shipping_address.city}, {order.shipping_address.country}\n"
                        f"Coupon Applied: {order.coupon.coupon_code if order.coupon else 'None'}\n\n"
                        f"Items:\n{item_list}\n\n"
                        f"Thank you for shopping with us!"
                    )

                    try:
                        send_mail(
                            subject=subject,
                            message=message,
                            from_email=settings.DEFAULT_FROM_EMAIL,
                            recipient_list=[order.user.email],
                            fail_silently=False,
                        )
                        status_val = 'sent'
                        error_message = None
                    except Exception as e:
                        status_val = 'failed'
                        error_message = str(e)

                    Notification.objects.create(
                        user=order.user,
                        notification_type='order_confirmation',
                        order=order,
                        subject=subject,
                        message=message,
                        status=status_val,
                        error_message=error_message
                    )

                    return Response({"status": True, "order_id": order.order_id}, status=status.HTTP_200_OK)
            
            return Response({"status": False, "message": "Payment verification failed"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"status": False, "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)