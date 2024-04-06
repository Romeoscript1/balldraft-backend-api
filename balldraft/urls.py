from django.contrib import admin
from django.urls import path, include

from contests import router as contests_api_router
from accounts import router as profile_api_router

contests_url_patterns = [
    path('contests/', include(contests_api_router.router.urls))
]

contests_url_patterns = [
    path('profile/', include(profile_api_router.router.urls))
]

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/auth/', include('accounts.urls')),
    path('api/v1/auth/', include('social_accounts.urls')),
    path('api/contest/', include('contests.urls')),
    path('api/', include(contests_url_patterns)),
]