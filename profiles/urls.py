from django.urls import path
from .views import (ProfileView, EmailChangeView, NotificationListView, mark_as_read, delete_notification)


urlpatterns=[
    path('', ProfileView.as_view(), name="profile"),
    path('change-email', EmailChangeView.as_view(), name='change-email'),
    path('notifications', NotificationListView.as_view(), name='notification-list'),
    path('notifications/<int:pk>/read', mark_as_read, name='notification-mark-as-read'),
    path('notifications/<int:pk>/delete', delete_notification, name='notification-delete'),
    path('referrals', ReferralListView.as_view(), name='referral-list'),
    path('referrals/create', ReferralCreateView.as_view(), name='referral-create'),
    path('referrals/<int:pk>', ReferralDetailView.as_view(), name='referral-detail'),

   
]

