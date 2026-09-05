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
    # Auth endpoints (matched with Frontend)
    path('auth/register/', register_user, name='register'),
    path('auth/login/', TokenObtainPairView.as_view(), name='login'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Alternative routes
    path('register/', register_user, name='register_alt'),
    path('login/', TokenObtainPairView.as_view(), name='login_alt'),

    # Passwordless OTP endpoints
    path('auth/send-email-otp/', send_email_otp, name='send_email_otp'),
    path('auth/verify-email-otp/', verify_email_otp, name='verify_email_otp'),
    path('auth/send-phone-otp/', send_phone_otp, name='send_phone_otp'),
    path('auth/verify-phone-otp/', verify_phone_otp, name='verify_phone_otp'),

    # TripSync features
    path('trips/', TripListCreateView.as_view(), name='trip_list_create'),
    path('preferences/', MemberPreferenceCreateView.as_view(), name='preferences'),
    path('trips/<int:trip_id>/itinerary/', ItineraryGenerateView.as_view(), name='itinerary'),
    path('trips/<int:trip_id>/expenses/', ExpenseListCreateView.as_view(), name='expenses'),
    path('reviews/', ReviewCreateView.as_view(), name='reviews'),
]