from rest_framework import serializers
from .models import Notification
from accounts.models import CustomUser
from orders.models import Order

class NotificationSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    order_id = serializers.CharField(source='order.order_id', read_only=True)

    class Meta:
        model = Notification
        fields = ['id', 'user', 'user_email', 'notification_type', 'order', 'order_id', 'subject', 'message', 'sent_at', 'status', 'error_message']
        read_only_fields = ['sent_at', 'status', 'error_message']