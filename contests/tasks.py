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
            response = requests.get(f"https://api.balldraft.com/search-fixtures?keyword={id}&limit=1")
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
                "https://api.balldraft.com/calculate-points/",
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



# @shared_task
# def algorithms_for_distribution():
#     """
#     - get all ContestHistory.objects.filter(positions=False && completed=True)
#     - get the game_id of  a contesthistory, then check if there're other types of
#     such fixtures in the db, that the game_id are same, then gather then all
#     - run a get request to this "https://api.balldraft.com/search-fixtures?keyword={game_id}&limit=1" 
#     - if there's a response, check if the current_entry value is == to the max_entry value, if false, then
#             Return the entry_amount to the won_amount field in the contesthistory model
#             and send an email that the contest was filled, so all contests are refunded
#             and don't continue
#       if the condition is true, meaning [current_entry==max_entry], then continue with the below algorithms
#     - look through and note, the 1. entry_amount, total_win_amount in the response gotten from the get request to the api
#     - then also go through the contesthistory instances were working on, then gather the values in the 'total_points'
#     field, and arrange them by adding an identifier to each value, then sort them by the highest to the lowest, 
#     then from the highest, after that, start awarding them positions in the "position" field in each contesthistory instance
#     remember the highest point is the first position, then second, then third and so on,

    
#     """
#     pass


@shared_task
def algorithms_for_distribution_position():
    try:
        pending_contests = ContestHistory.objects.filter(positions=False, completed=True)
        
        for contest in pending_contests:
            game_id = contest.game_id
            related_contests = ContestHistory.objects.filter(game_id=game_id)
            
            response = requests.get(f"https://api.balldraft.com/search-fixtures?keyword={game_id}&limit=1")
            response.raise_for_status()
            data = response.json()

            if not data['total_fixtures']:
                logger.warning(f"No unique fixture found for game_id {game_id}")
                continue

            fixture = data['fixtures'][0]
            current_entry = fixture.get('current_entry')
            max_entry = fixture.get('max_entry')

            # if current_entry != max_entry:
            #     for related_contest in related_contests:
            #         related_contest.won_amount = related_contest.entry_amount
            #         related_contest.positions = True
            #         related_contest.save()

            #         send_email(
            #             subject="Contest Refund Notification",
            #             body="The contest was not filled. All entry amounts have been refunded.",
            #             recipient=related_contest.profile.user.email
            #         )
            #     continue  # Do not proceed further if the condition is true
            
            # If current_entry == max_entry, proceed with the distribution algorithm
            total_win_amount = Decimal(fixture.get('total_win_amount', '0'))
            total_points = [
                (contest.id, contest.total_points)
                for contest in related_contests
            ]

            total_points.sort(key=lambda x: x[1], reverse=True)

            position = 1
            for contest_id, points in total_points:
                related_contest = ContestHistory.objects.get(id=contest_id)
                related_contest.position = position
                related_contest.positions = True
                related_contest.save()
                position += 1

    except requests.RequestException as e:
        logger.error(f"Request failed: {e}")
    except Exception as e:
        logger.error(f"An error occurred: {e}")


## production code
@shared_task
def distribute_profits_to_contests():
    try:
        pending_contests = ContestHistory.objects.filter(positions=True, profit=False, completed=True)
        logger.info(f"Pending contests: {pending_contests}")

        for contest in pending_contests:
            game_id = contest.game_id
            related_contests = ContestHistory.objects.filter(game_id=game_id, positions=True, profit=False, completed=True)
            logger.info(f"Related contests for game_id {game_id}: {related_contests}")

            entry_amount = contest.entry_amount
            max_entry = contest.max_entry
            pool_price = contest.pool_price

            if max_entry == 2:
                total_points = sorted([(c.id, c.total_points) for c in related_contests], key=lambda x: x[1], reverse=True)
                logger.info(f"Total points for max_entry 2: {total_points}")

                if total_points[0][1] == total_points[1][1] and total_points[0][1] != 0:
                    winner = ContestHistory.objects.get(id=total_points[0][0])
                    winner.won_amount += Decimal(0.9 * pool_price)
                    winner.profit = True
                    winner.save()
                    send_email(
                        subject="H2H Contest Winner Notification",
                        body=f"Congratulations! You have won the H2H contest of ₦{winner.won_amount}.",
                        recipient=winner.profile.user.email
                    )

                    loser = ContestHistory.objects.get(id=total_points[1][0])
                    loser.profit = True
                    loser.save()
                    send_email(
                        subject="H2H Contest Loser Notification",
                        body="Unfortunately, you did not win the H2H contest on Balldraft, Try again to win more than ₦10,000,000 on balldraft.",
                        recipient=loser.profile.user.email
                    )
                else:
                    # If points are not equal, handle as usual
                    winner = ContestHistory.objects.get(id=total_points[0][0])
                    winner.won_amount += Decimal(0.9 * pool_price)
                    winner.profit = True
                    winner.save()
                    send_email(
                        subject="H2H Contest Winner Notification",
                        body=f"Congratulations! You have won the H2H contest of ₦{winner.won_amount}.",
                        recipient=winner.profile.user.email
                    )

                    loser = ContestHistory.objects.get(id=total_points[1][0])
                    loser.profit = True
                    loser.save()
                    send_email(
                        subject="H2H Contest Loser Notification",
                        body="Unfortunately, you did not win the H2H contest on Balldraft, Try again to win more than ₦10,000,000 on balldraft.",
                        recipient=loser.profile.user.email
                    )

                continue  # Skip the rest of the loop

            # Prize distribution for contests with max_entry != 2
            total_points = sorted([(c.id, c.total_points) for c in related_contests], key=lambda x: x[1], reverse=True)
            logger.info(f"Total points for other contests: {total_points}")

            position_map = {
                1: (1, 10000, 15000, 25000, 50000, 75000, 100000, 300000, 1000000),
                2: (1, 7500, 10000, 15000, 25000, 50000, 75000, 250000, 750000),
                3: (1, 5000, 7500, 10000, 15000, 25000, 50000, 200000, 500000),
                4: (4, 600, 1500, 3000, 7500, 15000, 30000, 150000, 350000),
                5: (501, 400, 1000, 2000, 5000, 10000, 20000, 100000, 300000),
                6: (1351, 200, 500, 1000, 2500, 5000, 10000, 50000, 250000),
                7: (1851, 100, 250, 500, 1250, 2500, 5000, 25000, 125000),
                8: (2476, 75, 125, 250, 625, 1250, 2500, 12500, 62500),
                9: (2976, 50, 0, 250, 0, 0, 0, 0, 0)
            }

            for position, (start, *amounts) in position_map.items():
                if entry_amount == 200 and pool_price == 1000000 and max_entry == 5000:
                    prize = amounts[0]
                elif entry_amount == 500 and pool_price == 1000000 and max_entry == 2000:
                    prize = amounts[1]
                elif entry_amount == 1000 and pool_price == 1000000 and max_entry == 1000:
                    prize = amounts[2]
                elif entry_amount == 2500 and pool_price == 1000000 and max_entry == 400:
                    prize = amounts[3]
                elif entry_amount == 5000 and pool_price == 2000000 and max_entry == 400:
                    prize = amounts[4]
                elif entry_amount == 10000 and pool_price == 4000000 and max_entry == 400:
                    prize = amounts[5]
                elif entry_amount == 50000 and pool_price == 5000000 and max_entry == 100:
                    prize = amounts[6]
                elif entry_amount == 250000 and pool_price == 5000000 and max_entry == 20:
                    prize = amounts[7]
                else:
                    continue

                for index, (contest_id, _) in enumerate(total_points[start - 1:], start):
                    related_contest = ContestHistory.objects.get(id=contest_id)
                    related_contest.position = index
                    related_contest.won_amount += Decimal(prize)
                    related_contest.profile.account_balance += float(prize)
                    related_contest.profit = True
                    related_contest.save()
                    send_email(
                        subject="Multiple Entry Contest Notification || BALLDRAFT",
                        body=f"Your Contest Of ₦{related_contest.entry_amount} On BALLDRAFT Has Recently Completed, And You Got The [{related_contest.position}]TH Position, Kindly Log On To Your Account !!!",
                        recipient=related_contest.profile.user.email
                    )


            # Mark all related contests as having profit calculated
            for related_contest in related_contests:
                related_contest.profit = True
                related_contest.save()

    except requests.RequestException as e:
        logger.error(f"Request failed: {e}")
    except Exception as e:
        logger.error(f"An error occurred: {e}")
