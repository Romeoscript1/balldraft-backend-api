from django.urls import path
from .views import *

urlpatterns = [
    path('contest-history/', ContestHistoryCreateView.as_view(), name='contest_history_create'),
    path('contest-history/<int:pk>/', ContestHistoryDetailView.as_view(), name='contest_history_detail'),
    path('contest-history/list/', ContestHistoryListView.as_view(), name='contest_history_list'),
    path('slider/', SliderListCreateView.as_view(), name='slider-list-create'),
    path('slider/<int:pk>/', SliderDetailView.as_view(), name='slider-detail'),


]
