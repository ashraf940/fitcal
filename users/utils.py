# users/utils.py
import random
from django.utils import timezone
from datetime import timedelta
from django.conf import settings
from django.core.mail import send_mail

from .models import EmailOTP

def generate_numeric_otp(length=6):
    return "".join(str(random.randint(0,9)) for _ in range(length))

def create_and_send_otp(user, method="email"):
    """
    Create OTP record, send via email
    """
    code = generate_numeric_otp(6)
    now = timezone.now()
    expires = now + timedelta(minutes=10)
    otp = EmailOTP.objects.create(user=user, code=code, expires_at=expires)

    # Send email
    subject = "Your FitCal verification code"
    message = f"Your FitCal verification code is: {code}. It expires in 10 minutes."
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [user.email]
    send_mail(subject, message, from_email, recipient_list, fail_silently=False)

    return otp
