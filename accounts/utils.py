from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from .models import User, OneTimePassword
from django.conf import settings

import secrets

def generate_otp(length=6, characters="123456789"):
    """
    Generate a random One-Time Password (OTP) of specified length.

    By default, the OTP will be of length 6 and will only contain digits.
    However, the length and characters can be customized as per requirements.

    Parameters:
    length (int): The length of the OTP. Default is 6.
    characters (str): The characters to use for generating the OTP. Default is "123456789".

    Returns:
    str: The generated OTP.
    """
    return ''.join(secrets.choice(characters) for _ in range(length))

def send_code_to_user(email):
    try:
        user = get_object_or_404(User, email=email)
    except User.DoesNotExist:
        return False, "User with this email does not exist."

    subject = "One time password for Email verification"
    otp_code = generate_otp()
    print(otp_code)

    current_site = 'balldraft.com'
    email_body = f"Hello {user.first_name},\n Thanks for signing up on {current_site}. Here is your otp to verify your email -- {otp_code}."
    from_email = settings.DEFAULT_FROM_EMAIL

    try:
        otp, created = OneTimePassword.objects.get_or_create(user=user, defaults={'code': otp_code})
        if not created:
            otp.code = otp_code
            otp.save()
    except Exception as e:
        return False, f"Error while creating or updating OTP: {str(e)}"

    try:
        send_mail(
            subject=subject,
            message=email_body,
            from_email=from_email,
            recipient_list=[email],
            fail_silently=True
        )
    except Exception as e:
        return False, f"Error while sending email: {str(e)}"

    return True, "OTP sent successfully."

def send_reset_password_email(data):
    """
    Send reset password email to the user.

    Args:
        data (dict): A dictionary containing email details.
            'from_email' (str): The sender's email address.
            'to_email' (str): The recipient's email address.
            'email_subject' (str): The subject of the email.
            'email_body' (str): The content of the email.
    """
    send_mail(
        subject=data['email_subject'],
        message=data['email_body'],
        from_email=data['from_email'],
        recipient_list=[data['to_email']],
        fail_silently=True,
    )