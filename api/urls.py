from django.urls import path
from .views import (
    register_user, RegisterView,
    send_email_otp, verify_email_otp,
    forgot_password_request, reset_password_confirm
)

urlpatterns = [
    path('auth/register/', register_user, name='register_user'),
    path('auth/login/', RegisterView.as_view(), name='login_user'),
    path('auth/send-email-otp/', send_email_otp, name='send_email_otp'),
    path('auth/verify-email-otp/', verify_email_otp, name='verify_email_otp'),
    path('auth/forgot-password-request/', forgot_password_request, name='forgot_password_request'),
    path('auth/reset-password-confirm/', reset_password_confirm, name='reset_password_confirm'),
]
