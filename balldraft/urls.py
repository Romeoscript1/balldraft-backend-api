from django.contrib import admin
from django.urls import path, include

from contests import router as contests_api_router
from profiles import router as profile_api_router

from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework import permissions

schema_view = get_schema_view(
   openapi.Info(
      title="BallDraft API",
      default_version='v1',
      description="Control endpoint for functionalities in Balldraft",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@snippets.local"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=[permissions.AllowAny],
)

# contests_url_patterns = [
#     path('contests/', include(contests_api_router.router.urls))
# ]

# profile_url_patterns = [
#     path('profile/', include(profile_api_router.router.urls))
# ]

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/auth/', include('accounts.urls')),
    path('api/v1/auth/', include('social_accounts.urls')),
    path('api/v1/profile/', include('profiles.urls')),
    path('api/v1/contest/', include('contests.urls')),

    #documentation url
    path('docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]