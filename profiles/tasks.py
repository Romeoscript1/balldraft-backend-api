import logging
from celery import shared_task
from django.conf import settings
from paystackapi.transaction import Transaction
from .models import Payment, TransactionHistory

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

            # Log the transaction history for successful payment
            TransactionHistory.objects.create(
                profile=payment.profile,
                action=f"Deposit of NGN {payment.ngn_amount} verified",
                action_title="Deposit Successful!",
                category="Deposit"
            )
            logger.info(f"Payment {payment.reference} verified successfully")
        else:
            payment.status = 'failed'
        payment.save()
