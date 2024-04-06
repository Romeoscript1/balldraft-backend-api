from django.urls import path
from contests.views import EnterContest

urlpatterns = [
    path('contests/<int:contest_id>/enter/', EnterContest.as_view(), name='enter_contest'),
]
