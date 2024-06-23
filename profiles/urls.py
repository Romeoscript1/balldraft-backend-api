from django.urls import path
from .views import (ProfileView, EmailChangeView, NotificationListView, mark_as_read)


urlpatterns=[
    path('', ProfileView.as_view(), name="profile"),
    path('change-email', EmailChangeView.as_view(), name='change-email'),
    path('notifications', NotificationListView.as_view(), name='notification-list'),
    path('notifications/<int:pk>/read', mark_as_read, name='notification-mark-as-read'),


   
]

