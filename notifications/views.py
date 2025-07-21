from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.core.mail import send_mail
from django.conf import settings
from .models import Notification
from .serializers import NotificationSerializer
from orders.models import Order, OrderItem
from accounts.models import CustomUser

class SendOrderConfirmationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id)
            if order.user != request.user and not request.user.is_staff:
                return Response({"error": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)

            # Prepare email content
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

            # Send email
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

            # Save notification
            notification = Notification.objects.create(
                user=order.user,
                notification_type='order_confirmation',
                order=order,
                subject=subject,
                message=message,
                status=status_val,
                error_message=error_message
            )

            serializer = NotificationSerializer(notification)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

class NotificationListView(generics.ListAPIView):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAdminUser]

class NotificationDetailView(generics.RetrieveAPIView):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAdminUser]