import pyotp
import hashlib
import secrets
from django.core.mail import EmailMessage
from django.conf import settings
from .models import User, OneTimePassword
from datetime import timedelta
from django.utils import timezone

from django.conf import settings
from django.core.mail import send_mail

OTP_EXPIRATION_TIME_SECONDS = settings.OTP_EXPIRATION_TIME_SECONDS

import logging

logger = logging.getLogger(__name__)


def generate_otp():
    otp_characters = "123456789"
    otp_length = 6
    otp = ''.join(secrets.choice(otp_characters) for _ in range(otp_length))
    return otp

def hash_otp(otp):
    # Use a secure hashing algorithm
    return hashlib.sha256(otp.encode()).hexdigest()

def send_code_to_user(email):
    subject = "One-time password for Email verification"
    otp_code = generate_otp()
    hashed_otp = hash_otp(otp_code)
    
    user = User.objects.get(email=email)
    current_site = 'balldraft.com'
    email_body = f"Hello {user.first_name}, \nThanks for signing up on {current_site}. Here is your OTP to verify your email: {otp_code}."
    from_email = settings.EMAIL_HOST_USER

    # Calculate expiration time for OTP
    expiration_time = timezone.now() + timedelta(seconds=OTP_EXPIRATION_TIME_SECONDS)

    # Save hashed OTP in the database using email
    OneTimePassword.objects.create(email=user.email, code=hashed_otp, expires_at=expiration_time)

    send_email = EmailMessage(subject=subject, body=email_body, from_email=from_email, to=[email])
    try:
        send_email.send(fail_silently=True)
        logger.debug("Opt sent")
        return "Otp Sent"
    except Exception as e:
        logger.debug(f"Couldn't send otp code to mail: {e}")
        return f"Couldn't send otp code to mail: {e}"


def send_reset_password_email(data):
    print(data['email_body'])
    email=EmailMessage(subject=data['email_subject'], body=data['email_body'], from_email=settings.EMAIL_HOST_USER, to=[data['to_email']])

    email.send(fail_silently=True)