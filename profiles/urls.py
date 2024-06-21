from django.urls import path
from .views import (ProfileView, EmailChangeView)


urlpatterns=[
    path('', ProfileView.as_view(), name="profile"),
    path('change-email/', EmailChangeView.as_view(), name='change-email'),

   
]

