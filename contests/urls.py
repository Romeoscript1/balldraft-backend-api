from django.urls import path
from .views import ContestHistoryCreateView, ContestHistoryDetailView, ContestHistoryListView, ContestHistoryUpdateView

urlpatterns = [
    path('contest-history/', ContestHistoryCreateView.as_view(), name='contest_history_create'),
    path('contest-history/<int:pk>/', ContestHistoryDetailView.as_view(), name='contest_history_detail'),
    path('contest-history/list/', ContestHistoryListView.as_view(), name='contest_history_list'),

]
