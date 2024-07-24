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



# @shared_task
# def algorithms_for_distribution():
#     """
#     - get all ContestHistory.objects.filter(positions=False && completed=True)
#     - get the game_id of  a contesthistory, then check if there're other types of
#     such fixtures in the db, that the game_id are same, then gather then all
#     - run a get request to this "http://127.0.0.1:8000/search-fixtures?keyword={game_id}&limit=1" 
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
            
            response = requests.get(f"http://127.0.0.1:8000/search-fixtures?keyword={game_id}&limit=1")
            response.raise_for_status()
            data = response.json()

            if not data['total_fixtures']:
                logger.warning(f"No unique fixture found for game_id {game_id}")
                continue

            fixture = data['fixtures'][0]
            current_entry = fixture.get('current_entry')
            max_entry = fixture.get('max_entry')

            if current_entry != max_entry:
                for related_contest in related_contests:
                    related_contest.won_amount = related_contest.entry_amount
                    related_contest.positions = True
                    related_contest.save()

                    send_email(
                        subject="Contest Refund Notification",
                        body="The contest was not filled. All entry amounts have been refunded.",
                        recipient=related_contest.profile.user.email
                    )
                continue  # Do not proceed further if the condition is true
            
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


# @shared_task
# def distribute_profits_to_contests():
#     """
#     - use this algorithm to write the code that would help distribute profits effectively
#     - firstly  get all ContestHistory.objects.filter(positions=True && profit=False && completed=True)
#     -  get the game_id of  a contesthistory, then check if there're other types of
#      such fixtures in the db, and that also satisfies this conditions [ontestHistory.objects.filter(positions=True && profit=False && completed=True)] that the game_id are same, then gather then all
#     - then get the entry_amount, max_entry and the pool_price of the instance.
#     if the max_entry==2, then:
#         arrange the total_points,
#         if total_points of user1 == total_points of user2 and it's values are not 0 or 0.00:
#             then
#                 add to the user with the highest point and it's "position" is 1,
#                 add won_amount += 0.9(pool_price)
#                 send an email that they won the H2H contest with the details of the contest
#             then also:
#                 to the user with position 2, and lower point in the total_points,
#                 add nothing to then, 
#                 send them an email that they lost the H2H contest and details of the contest too

#     else [meaning that the max_entry is != 2]:
#         ## we'd be writing 8 conditional statements to match the conditions for profit distributions
#         condition1:
#         if entry_amount == 200 && pool_price == 1000000 && max_entry == 5000:
#             give instance with position 1, 10000 and add it to the won_amount field,
#             also give instance with position 2,  7500 and add it to the won_amount field,
#             also give instance with position 3, 5000 and add it to the won_amount field,
#             also give also instance with position starting at 4-500,  600 and add it to the won_amount field,
#             also give also instance with position starting at 501-1350,  400 and add it to the won_amount field,
#             also give also instance with position starting at 1351-1850,  200 and add it to the won_amount field,
#             also give also instance with position starting at 1851-2475,  100 and add it to the won_amount field,
#             also give also instance with position starting at 2476-2975,  75 and add it to the won_amount field,
#             also give also instance with position starting at 2976-3725,  50 and add it to the won_amount field,
#             and that's all, then lastly, mark the field "field profit=True"
        
#         condition2:
#         elif entry_amount == 500 && pool_price == 1000000 && max_entry == 2000:
#             give instance with position 1, 15000 and add it to the won_amount field,
#             also give instance with position 2,  10000 and add it to the won_amount field,
#             also give instance with position 3, 7500 and add it to the won_amount field,
#             also give also instance with position starting at 4-203,  1500 and add it to the won_amount field,
#             also give also instance with position starting at 204-588,  1000 and add it to the won_amount field,
#             also give also instance with position starting at 589-793,  500 and add it to the won_amount field,
#             also give also instance with position starting at 794-993,  250 and add it to the won_amount field,
#             also give also instance with position starting at 994-1233,  125 and add it to the won_amount field,
#             and that's all, then lastly, mark the field "field profit=True"


#         condition3:
#         elif entry_amount == 1000 && pool_price == 1000000 && max_entry == 1000:
#             give instance with position 1, 25000 and add it to the won_amount field,
#             also give instance with position 2,  15000 and add it to the won_amount field,
#             also give instance with position 3, 10000 and add it to the won_amount field,
#             also give also instance with position starting at 4-53,  3000 and add it to the won_amount field,
#             also give also instance with position starting at 54-303,  2000 and add it to the won_amount field,
#             also give also instance with position starting at 304-403,  1000 and add it to the won_amount field,
#             also give also instance with position starting at 404-513,  500 and add it to the won_amount field,
#             also give also instance with position starting at 514-693,  250 and add it to the won_amount field,
#             and that's all, then lastly, mark the field "field profit=True"


#         condition4:
#         elif entry_amount == 2500 && pool_price == 1000000 && max_entry == 400:
#             give instance with position 1, 50000 and add it to the won_amount field,
#             also give instance with position 2,  25000 and add it to the won_amount field,
#             also give instance with position 3, 15000 and add it to the won_amount field,
#             also give also instance with position starting at 4-28,  7500 and add it to the won_amount field,
#             also give also instance with position starting at 29-124,  5000 and add it to the won_amount field,
#             also give also instance with position starting at 125-151,  2500 and add it to the won_amount field,
#             also give also instance with position starting at 152-176,  1250 and add it to the won_amount field,
#             also give also instance with position starting at 177-246,  625 and add it to the won_amount field,
#             and that's all, then lastly, mark the field "field profit=True"


#         condition5:
#         elif entry_amount == 5000 && pool_price == 2000000 && max_entry == 400:
#             give instance with position 1, 75000 and add it to the won_amount field,
#             also give instance with position 2,  50000 and add it to the won_amount field,
#             also give instance with position 3, 25000 and add it to the won_amount field,
#             also give also instance with position starting at 4-28,  15000 and add it to the won_amount field,
#             also give also instance with position starting at 29-123,  10000 and add it to the won_amount field,
#             also give also instance with position starting at 124-153,  5000 and add it to the won_amount field,
#             also give also instance with position starting at 154-178,  2500 and add it to the won_amount field,
#             also give also instance with position starting at 179-268,  1250 and add it to the won_amount field,
#             and that's all, then lastly, mark the field "field profit=True"


#         condition6:
#         elif entry_amount == 10000 && pool_price == 4000000 && max_entry == 400:
#             give instance with position 1, 10000 and add it to the won_amount field,
#             also give instance with position 2,  75000 and add it to the won_amount field,
#             also give instance with position 3, 50000 and add it to the won_amount field,
#             also give also instance with position starting at 4-28,  30000 and add it to the won_amount field,
#             also give also instance with position starting at 29-118,  20000 and add it to the won_amount field,
#             also give also instance with position starting at 119-150,  10000 and add it to the won_amount field,
#             also give also instance with position starting at 151-201,  5000 and add it to the won_amount field,
#             also give also instance with position starting at 202-301,  2500 and add it to the won_amount field,
#             and that's all, then lastly, mark the field "field profit=True"


#         condition7:
#         elif entry_amount == 50000 && pool_price == 5000000 && max_entry == 100:
#             give instance with position 1, 250000 and add it to the won_amount field,
#             also give instance with position 2,  150000 and add it to the won_amount field,
#             also give instance with position 3, 100000 and add it to the won_amount field,
#             also give also instance with position starting at 4-8,  150000 and add it to the won_amount field,
#             also give also instance with position starting at 9-34,  100000 and add it to the won_amount field,
#             also give also instance with position starting at 35-41,  50000 and add it to the won_amount field,
#             also give also instance with position starting at 42-48,  25000 and add it to the won_amount field,
#             also give also instance with position starting at 49-60,  12500 and add it to the won_amount field,
#             and that's all, then lastly, mark the field "field profit=True"




#         condition8:
#         elif entry_amount == 250000 && pool_price == 5000000 && max_entry == 20:
#             give instance with position 1, 1000000 and add it to the won_amount field,
#             also give instance with position 2,  750000 and add it to the won_amount field,
#             also give instance with position 3, 500000 and add it to the won_amount field,
#             also give also instance with position starting at 4-8,  350000 and add it to the won_amount field,
#             also give also instance with position starting at 9-11,  300000 and add it to the won_amount field,
#             also give also instance with position at 12,  250000 and add it to the won_amount field,
#            and that's all, then lastly, mark the field "field profit=True"



    
#     """
#     pass


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
                        body="Congratulations! You have won the H2H contest.",
                        recipient=winner.profile.user.email
                    )

                    loser = ContestHistory.objects.get(id=total_points[1][0])
                    loser.profit = True
                    loser.save()
                    send_email(
                        subject="H2H Contest Loser Notification",
                        body="Unfortunately, you did not win the H2H contest.",
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
                        body="Congratulations! You have won the H2H contest.",
                        recipient=winner.profile.user.email
                    )

                    loser = ContestHistory.objects.get(id=total_points[1][0])
                    loser.profit = True
                    loser.save()
                    send_email(
                        subject="H2H Contest Loser Notification",
                        body="Unfortunately, you did not win the H2H contest.",
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
                    related_contest.profit = True
                    related_contest.save()

            # Mark all related contests as having profit calculated
            for related_contest in related_contests:
                related_contest.profit = True
                related_contest.save()

    except requests.RequestException as e:
        logger.error(f"Request failed: {e}")
    except Exception as e:
        logger.error(f"An error occurred: {e}")
