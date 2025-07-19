import random
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from .models import OTPVerification

def generate_otp():
    return ''.join(random.choices('0123456789', k=6))

def send_otp_email(user, purpose):
    otp = generate_otp()
    expires_at = timezone.now() + timedelta(minutes=10)
    OTPVerification.objects.create(
        user=user,
        code=otp,
        purpose=purpose,
        expires_at=expires_at
    )
    subject = 'Your OTP Code' if purpose == 'email_verification' else 'Password Reset OTP'
    message = f'Your OTP code is {otp}. It expires in 10 minutes.'
    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        [user.email],
        fail_silently=False,
    )