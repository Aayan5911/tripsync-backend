from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    register_user,
    TripListCreateView,
    MemberPreferenceCreateView,
    ItineraryGenerateView,
    ExpenseListCreateView,
    ReviewCreateView,
    send_email_otp,
    verify_email_otp,
    send_phone_otp,
    verify_phone_otp,
)

urlpatterns = [
    # Auth endpoints (with /auth/ prefix)
    path('auth/register/', register_user, name='register'),
    path('auth/register', register_user, name='register_noslash'),
    path('auth/login/', TokenObtainPairView.as_view(), name='login'),
    path('auth/login', TokenObtainPairView.as_view(), name='login_noslash'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Direct endpoints (without /auth/ prefix)
    path('register/', register_user, name='register_alt'),
    path('register', register_user, name='register_alt_noslash'),
    path('login/', TokenObtainPairView.as_view(), name='login_alt'),
    path('login', TokenObtainPairView.as_view(), name='login_alt_noslash'),

    # Email OTP endpoints (All variations)
    path('auth/send-email-otp/', send_email_otp, name='send_email_otp'),
    path('auth/send-email-otp', send_email_otp, name='send_email_otp_noslash'),
    path('send-email-otp/', send_email_otp, name='send_email_otp_direct'),
    path('send-email-otp', send_email_otp, name='send_email_otp_direct_noslash'),

    path('auth/verify-email-otp/', verify_email_otp, name='verify_email_otp'),
    path('auth/verify-email-otp', verify_email_otp, name='verify_email_otp_noslash'),
    path('verify-email-otp/', verify_email_otp, name='verify_email_otp_direct'),
    path('verify-email-otp', verify_email_otp, name='verify_email_otp_direct_noslash'),

    # Phone OTP endpoints
    path('auth/send-phone-otp/', send_phone_otp, name='send_phone_otp'),
    path('auth/send-phone-otp', send_phone_otp, name='send_phone_otp_noslash'),
    path('send-phone-otp/', send_phone_otp, name='send_phone_otp_direct'),
    path('send-phone-otp', send_phone_otp, name='send_phone_otp_direct_noslash'),

    path('auth/verify-phone-otp/', verify_phone_otp, name='verify_phone_otp'),
    path('auth/verify-phone-otp', verify_phone_otp, name='verify_phone_otp_noslash'),
    path('verify-phone-otp/', verify_phone_otp, name='verify_phone_otp_direct'),
    path('verify-phone-otp', verify_phone_otp, name='verify_phone_otp_direct_noslash'),

    # TripSync features
    path('trips/', TripListCreateView.as_view(), name='trip_list_create'),
    path('trips', TripListCreateView.as_view(), name='trip_list_create_noslash'),
    path('preferences/', MemberPreferenceCreateView.as_view(), name='preferences'),
    path('trips/<int:trip_id>/itinerary/', ItineraryGenerateView.as_view(), name='itinerary'),
    path('trips/<int:trip_id>/expenses/', ExpenseListCreateView.as_view(), name='expenses'),
    path('reviews/', ReviewCreateView.as_view(), name='reviews'),
]