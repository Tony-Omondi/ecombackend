from django.db import models
from accounts.models import CustomUser
from orders.models import Order

class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('order_confirmation', 'Order Confirmation'),
        ('general', 'General'),
    )

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='sent')  # sent, failed
    error_message = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.notification_type} to {self.user.email} at {self.sent_at}"