import random
from django.core.mail import EmailMessage
from django.conf import settings

import pyotp

def send_verification_email(user, secret):
    totp = pyotp.TOTP(secret)
    otp = totp.now()
    
    email_subject = 'Verify your Email Address'
    email_body = f"Hello {user.first_name},\n\nPlease verify your email address by entering the following code:\n\nOTP: {otp}\n\nThank you!"
    from_email = settings.DEFAULT_FROM_EMAIL
    
    send_email = EmailMessage(subject=email_subject, body=email_body, from_email=from_email, to=[user.email])
    send_email.send(fail_silently=True)


def send_reset_password_email(data):
    email=EmailMessage(subject=data['email_subject'], body=data['email_body'], from_email=settings.EMAIL_HOST_USER, to=[data['to_email']])

    email.send(fail_silently=True)
