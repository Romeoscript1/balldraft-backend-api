# tasks.py
import requests
from celery import shared_task
from django.utils import timezone
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
            id = c.game_id 
            fixture_id = c.fixture_id
            response = requests.get(f"http://127.0.0.1:8000/search-fixtures?keyword={id}&limit=1")
            response.raise_for_status()
            data = response.json()

            if not data['total_fixtures']:
                print("Currently in this section!!!")
                logger.warning(f"No unique fixture found for ID {id}")
                continue

            fixture = data['fixtures'][0]

            if not fixture['completed']:
                logger.info(f"Fixture {fixture_id} is not completed yet.")
                continue

            related_contests = ContestHistory.objects.filter(fixture_id=fixture_id)

            # Prepare data for points calculation
            players_data = {
                f"user{contest.profile.user.id}": {
                    "players": [player.player_id for player in contest.players.all()],
                    "entry_time": contest.entered_by.isoformat()
                }
                
                for contest in related_contests
            }

            logger.info(f"Player Details: {players_data}")
            request_body = {
                "contest_title": fixture['title'],
                "fixture_id": fixture_id,
                "selected_players": players_data
            }


            logger.info(f"Request Body: {request_body}")

            points_response = requests.post(
                "http://127.0.0.1:8000/calculate-points/",
                json=request_body
            )

            points_response.raise_for_status()
            points_data = points_response.json()
            logger.info(f"Points Data: {points_data}")

            for contest in related_contests:
                user_key = f"user{contest.profile.user.id}"
                contest.total_points = points_data['scores'].get(user_key, 0)
                contest.completed = True
                contest.pending = False
                contest.pool_price = Decimal(fixture['total_to_win'])
                contest.league_name = fixture['league_name']
                contest.save()

                # send_email(
                #     subject=f"${contest.entry_amount} Fantasy Contest Completed!! | Balldraft LTD",
                #     body="Congratulations! Your contest has been completed.",
                #     recipient=contest.profile.user.email
                # )

    except requests.RequestException as e:
        logger.error(f"Request failed: {e}")
    except Exception as e:
        logger.error(f"An error occurred: {e}")



@shared_task
def algorithms_for_distribution():
    """
    - create a field [profit - True or False "False" ]
    - get all ContestHistory.objects.filter(profit=False && completed=True)
    - get an id of a fixture, fixture_id and not id, then check if there're other types of
    such fixtures in the db, then gather then all
    - look through and note, the 1. entry_amount, current_entry total_win_amount, max_entry
    - check if current_entry == max_entry
        if false:
            end
        else:
            run the algorithm func that performs the calculate of total_win_amount,
            looking at the points, and watching out for similar traits,and others
            sends an email 
            waits for another 30mins to execute it
    
    """
    pass

