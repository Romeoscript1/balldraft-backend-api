import logging
from celery import shared_task
from django.conf import settings
from paystackapi.transaction import Transaction
from .models import Payment, TransactionHistory, Deposit

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from random import shuffle
import logging

def send_email(subject, body, recipient):
    context = {
        "subject": subject,
        "body": body,
    }
    html_content = render_to_string("emails.html", context)
    text_content = strip_tags(html_content)
    email = EmailMultiAlternatives(
        subject,
        text_content,
        settings.EMAIL_HOST_USER,
        [recipient]
    )
    email.attach_alternative(html_content, 'text/html')
    email.send()

logger = logging.getLogger(__name__)

@shared_task
def verify_pending_payments():
    unverified_payments = Payment.objects.filter(status__in=['pending', 'failed'])

    for payment in unverified_payments:
        # Verify Paystack transaction
        response = Transaction.verify(payment.reference)
        if not response['status']:
            logger.error(f"Unable to verify Paystack transaction for reference {payment.reference}")
            continue

        # Update payment status
        if response['data']['status'] == 'success':
            payment.status = 'success'
            payment.profile.account_balance += float(payment.ngn_amount)
            payment.profile.save()

            subject = "Balldraft | Account Funding Successful"
            message = f"Your Deposit of {payment.ngn_amount} Is Successful, The Funds have arrived in your balance"
            recipient_list = payment.profile.email  
            
            send_email(
                        subject,
                        message,
                        recipient_list
                    )

            # Log the transaction history for successful payment
            TransactionHistory.objects.create(
                profile=payment.profile,
                action=f"Deposit of NGN {payment.ngn_amount} verified",
                action_title="Deposit Successful!",
                category="Deposit"
            )

            Deposit.objects.create(
                    profile=payment.profile,
                    ngn_amount = payment.ngn_amount,
                    verified = True
                )

            logger.info(f"Payment {payment.reference} verified successfully")
        else:
            payment.status = 'failed'
        payment.save()
