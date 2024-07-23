import requests
from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from .models import ContestHistory
from decimal import Decimal
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from random import shuffle
import logging

logger = logging.getLogger(__name__)

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


@shared_task
def update_contest_history():
    try:
        for c in ContestHistory.objects.filter(pending=True):
            id = c.id 
            response = requests.get(f"http://127.0.0.1:8000/search-fixtures?keyword={id}&limit=1")
            response.raise_for_status()
            data = response.json()

            if data['total_fixtures'] != 1:
                logger.warning(f"No unique fixture found for ID {id}")
                continue

            fixture = data['fixtures'][0]

            if not fixture['completed']:
                logger.info(f"Fixture {id} is not completed yet.")
                continue

            total_to_win = Decimal(fixture['total_to_win'])
            league_name = fixture['league_name']

            related_contests = ContestHistory.objects.filter(id=id)
            num_contests = related_contests.count()

            if num_contests == 0:
                logger.warning(f"No related contests found for fixture ID {id}")
                continue

            one_third = total_to_win / 3

            # First third: distribute among all contests
            shuffle(related_contests)
            for i, contest in enumerate(related_contests):
                if i == 0:
                    contest.won_amount = one_third * Decimal('0.75')
                elif i == 1:
                    contest.won_amount = one_third * Decimal('0.30')
                elif i == 2:
                    contest.won_amount = one_third * Decimal('0.20')
                else:
                    contest.won_amount = one_third / Decimal(num_contests - 3)

                contest.completed = True
                contest.pending = False
                contest.pool_price = total_to_win
                contest.league_name = league_name
                contest.save()

                send_email(
                    subject=f"${contest.entry_amount} Fantasy Contest Completed!! | Balldraft LTD",
                    body="Congratulations! Your contest has been completed.",
                    recipient=contest.profile.user.email
                )

            c.completed = True
            c.pending = False
            c.pool_price = total_to_win
            c.league_name = league_name
            c.save()

    except requests.RequestException as e:
        logger.error(f"Request failed: {e}")
    except Exception as e:
        logger.error(f"An error occurred: {e}")
