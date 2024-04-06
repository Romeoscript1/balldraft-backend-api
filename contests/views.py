from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from contests.models import Contest

class EnterContest(APIView):
    def post(self, request, contest_id):
        try:
            profile = request.user.profile
            contest = Contest.objects.get(id=contest_id)
            profile.contests.add(contest)
            return Response(status=status.HTTP_201_CREATED)
        except Contest.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)