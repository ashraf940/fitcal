from django.core.mail import send_mail
from django.conf import settings
from .models import EmailOTP
import random
from datetime import timedelta
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

def generate_numeric_otp(length=6):
    return "".join(str(random.randint(0, 9)) for _ in range(length))

def send_otp_email(subject, message, recipient_list):
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            recipient_list,
            fail_silently=False,
        )
        logger.info(f"OTP email bheja: {recipient_list}")
        return True
    except Exception as e:
        logger.error(f"OTP email nahi bheja: {recipient_list}, error: {str(e)}")
        return False

def create_and_send_otp(user):
    try:
        code = generate_numeric_otp(6)
        now = timezone.now()
        expires = now + timedelta(minutes=10)

        otp = EmailOTP.objects.create(user=user, code=code, expires_at=expires)

        subject = "Tumhara FitCal Verification Code"
        message = f"Tumhara code hai: {code}. Ye 10 minute mein expire ho jayega."
        recipient_list = [user.email]

        if send_otp_email(subject, message, recipient_list):
            return otp
        else:
            logger.error(f"Failed to send OTP to {user.email}")
            return None
    except Exception as e:
        logger.error(f"OTP banane mein error for {user.email}: {str(e)}")
        return None