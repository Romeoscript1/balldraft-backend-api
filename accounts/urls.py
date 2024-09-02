from django.urls import path
from .views import (RegisterUserView, 
                    VerifyUserEmail, 
                    PasswordResetConfirm, 
                    SetNewPassword, 
                    PasswordResetRequestView,
                    LogoutUserView,
                    ResendCodeView,
                    login_view,
                    
                    ActivateAccountView,
                    DeactivateAccountView,
                    DeleteAccountView,
                    
                    Enable2FAView,
                    Verify2FATokenView,
                    Disable2FAView)



urlpatterns=[
    path('register/', RegisterUserView.as_view(), name='register'),
    path('verify-email/', VerifyUserEmail.as_view(), name='verify-email'),
    path('resend-code/', ResendCodeView.as_view(), name='resend_code'),
    path('token/', login_view, name='login'),
    path('password-reset/', PasswordResetRequestView.as_view(), name='password-reset'),
    path('password-reset-confirm/<uidb64>/<token>', PasswordResetConfirm.as_view(), name='password_reset_confirm'),
    path('set-new-password/', SetNewPassword.as_view(), name='set_new_password'),
    path('logout/', LogoutUserView.as_view(), name='logout'),

    path('account/deactivate/', DeactivateAccountView.as_view(), name='deactivate-account'),
    path('account/activate/', ActivateAccountView.as_view(), name='activate-account'),
    path('account/delete/', DeleteAccountView.as_view(), name='delete-account'),

    path('2fa/enable/', Enable2FAView.as_view(), name='enable_2fa'),
    path('2fa/verify/', Verify2FATokenView.as_view(), name='verify_2fa'),
    path('2fa/disable/', Disable2FAView.as_view(), name='disable_2fa'),

]

