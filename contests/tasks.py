from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from .models import ContestHistory
from decimal import Decimal
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

##Sending Emails to Clients that their contest has completed
def send_email(subject,body,recipient):
    context ={
        "subject": subject,
        "body":body,
        }
    html_content = render_to_string("emails.html", context)
    text_content = strip_tags(html_content)
    email = EmailMultiAlternatives(
        subject,
        text_content,
        settings.EMAIL_HOST_USER ,
        [recipient]
    )
    email.attach_alternative(html_content, 'text/html')
    email.send()


@shared_task
def update_contest_history():
    for c in ContestHistory.objects.filter(pending=True):
        plan_end_date = plan.date_created + timedelta(days=plan.number_of_days)
        if timezone.now().date() >= plan_end_date:
            profile = plan.profile
            profile.available_balance += plan.amount + Decimal(plan.profit)
            profile.book_balance += plan.amount + Decimal(plan.profit)
            body = f"""
            Hello there, your Investment is matured and due for withdrawal from blisschain LTD, 
            kindly head over to your dashboard to request for a withdrawal.
            
            For any issues encountered with using our services, please don't hesitate to reach our to support through support@bliss-chain.com,
            or directly on our website.
            """
            send_email(f"${plan.amount} Investment Completed!! | BlissChain LTD", body, plan.profile.user.email)
            send_email(f"Alert!!, {plan.profile.user.username} Investment Completed today | BlissChain LTD", "the investment of the customer completed today, he invested ${plan.amount}, kindly checkup on them if they need any assistance", 'support@bliss-chain.com')
            profile.save()

            plan.done = True
            plan.save()