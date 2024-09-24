from django.urls import path
from .views import *


urlpatterns=[
    path('', ProfileView.as_view(), name="profile"),
    path('change-email/', EmailChangeView.as_view(), name='change-email'),
    path('notifications/', NotificationListView.as_view(), name='notification-list'),
    path('notifications/<int:pk>/read/', mark_as_read, name='notification-mark-as-read'),
    path('notifications/<int:pk>/delete/', delete_notification, name='notification-delete'),
    path('payments/create/', PaymentCreateView.as_view(), name='payment-create'),
    path('payments/verify/', PaymentVerifyView.as_view(), name='payment-verify'),
        path('withdrawals/verify/<str:reference>/', WithdrawVerifyView.as_view(), name='withdrawal-verify'),
    path('withdrawals/create/', WithdrawCreateView.as_view(), name='withdrawal-create'),
    path('transactions/', TransactionHistoryListView.as_view(), name='transaction-history-list'),
    path('transactions/<int:id>/', TransactionHistoryDetailView.as_view(), name='transaction-history-detail'),

    path('user-activity/', UserActivityView.as_view(), name='user-activity'),
    path('help/', HelpmeView.as_view(), name='help'),




   
]