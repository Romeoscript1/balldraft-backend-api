from django.urls import path
from .views import (
                    EmailChangeView, ProfileView)


urlpatterns=[
    path('', ProfileView.as_view(), name="profile"),
    path('change-email/', EmailChangeView.as_view(), name='change-email'),
]

# urlpatterns = format_suffix_patterns(urlpatterns)