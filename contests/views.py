from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Contest 
from profiles.models import ContestEntry

class EnterContest(APIView):
    def post(self, request, contest_id):
        try:
            profile = request.user.profile
            contest = Contest.objects.get(id=contest_id)
            
            # Check if game is live or not
            if contest.is_upcoming is True and contest.is_live is False:
                # Check if user balance is enough for contest
                if contest.entry_fee < profile.account_balance:
                    # Check if the contest allows multiple entries
                    if contest.allow_multiple_entries:
                        # Check if the user has reached the maximum number of entries
                        user_entries_count = ContestEntry.objects.filter(profile=profile, contest=contest).count()
                        if user_entries_count < contest.max_multi_entries:
                            # User can enter the contest again
                            ContestEntry.objects.create(profile=profile, contest=contest, entry_time=timezone.now())
                            # Deduct entry fee from user's account balance
                            profile.account_balance -= contest.entry_fee
                            profile.save()
                            return Response(status=status.HTTP_201_CREATED)
                        else:
                            return Response({"error": "Maximum entries reached for this contest."}, status=status.HTTP_400_BAD_REQUEST)
                    else:
                        # Check if the user has already entered the contest
                        if ContestEntry.objects.filter(profile=profile, contest=contest).exists():
                            return Response({"error": "You have already entered this contest."}, status=status.HTTP_400_BAD_REQUEST)
                        else:
                            # User can enter the contest
                            ContestEntry.objects.create(profile=profile, contest=contest, entry_time=timezone.now())
                            return Response(status=status.HTTP_201_CREATED) 
                else:
                    return Response({"error": "Account Balance not enough for contest. Deposit into your account."}, status=status.HTTP_400_BAD_REQUEST)
            else:
                    return Response({"error": "Game is ongoing already"}, status=status.HTTP_400_BAD_REQUEST)
        except Contest.DoesNotExist:
            return Response({"error": "Contest does not exist."}, status=status.HTTP_404_NOT_FOUND)
