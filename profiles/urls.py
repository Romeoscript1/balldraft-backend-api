from django.urls import path
from .views import (ProfileView, 
                    #update views
                    MobileNumberView, 
                    AddressView,
                    UserNameUpdateView,
                    EmailChangeView,)
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns=[
    # path('profile/', ProfileView.as_view(), name='profile'),

    #update urls
    path('profile/mobile-number/', MobileNumberView.as_view(), name='mobile-number'),
    path('profile/address/', AddressView.as_view(), name='address'),
    path('update-username/', UserNameUpdateView.as_view(), name='update-username'),
    path('change-email/', EmailChangeView.as_view(), name='change-email'),
]

urlpatterns = format_suffix_patterns(urlpatterns)