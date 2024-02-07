from django.urls import path
from .views import (RegisterUserView, 
                    VerifyUserEmail, 
                    LoginUserView,
                    PasswordResetConfirm, 
                    SetNewPassword, 
                    PasswordResetRequestView,
                    LogoutUserView)
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

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

urlpatterns=[
    path('register/', RegisterUserView.as_view(), name='register'),
    path('verify-email', VerifyUserEmail.as_view(), name='verify-email'),
    path('login/', LoginUserView.as_view(), name='login'),
    path('password-reset/', PasswordResetRequestView.as_view(), name='password-reset'),
    path('password_reset_confirm/<uidb64>/<token>', PasswordResetConfirm.as_view(), name='password_reset_confirm'),
    path('set-new-password/', SetNewPassword.as_view(), name='set_new_password'),
    path('logout/', LogoutUserView.as_view(), name='logout'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

urlpatterns = format_suffix_patterns(urlpatterns)