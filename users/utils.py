import random
from datetime import timedelta
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
import logging
from .models import EmailOTP

logger = logging.getLogger(__name__)

def generate_numeric_otp(length=6):
    return "".join(str(random.randint(0, 9)) for _ in range(length))

def send_otp_email(subject, message, recipient_list):
    try:
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list)
        logger.info(f"OTP sent to {recipient_list}")
        return True
    except Exception as e:
        logger.error(f"Failed to send OTP to {recipient_list}: {str(e)}")
        return False

def create_and_send_otp(user):
    code = generate_numeric_otp()
    expires = timezone.now() + timedelta(minutes=10)
    otp = EmailOTP.objects.create(user=user, code=code, expires_at=expires)
    subject = "Your FitCal Verification Code"
    message = f"Your OTP is: {code}. It will expire in 10 minutes."
    if send_otp_email(subject, message, [user.email]):
        return otp
    return None
