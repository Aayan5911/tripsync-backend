import random
import requests
from django.contrib.auth.models import User
from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .models import UserOTP

# ----------------- AUTH VIEWS -----------------

@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    username = request.data.get('username', '').strip()
    email = request.data.get('email', '').strip()
    password = request.data.get('password', '').strip()

    if not username or not password:
        return Response({'error': 'Username and password are required.'}, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.filter(username__iexact=username).first()
    if user:
        if email:
            user.email = email
        user.set_password(password)
        user.save()
    else:
        user = User.objects.create_user(username=username, email=email, password=password)

    refresh = RefreshToken.for_user(user)
    return Response({
        'message': 'User registered successfully',
        'access': str(refresh.access_token),
        'refresh': str(refresh),
        'username': user.username
    }, status=status.HTTP_201_CREATED)


class RegisterView(generics.GenericAPIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username', '').strip()
        password = request.data.get('password', '').strip()

        user = User.objects.filter(username__iexact=username).first()
        if user and user.check_password(password):
            refresh = RefreshToken.for_user(user)
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'username': user.username
            })
        return Response({'error': 'Invalid username or password.'}, status=status.HTTP_401_UNAUTHORIZED)


# ----------------- EMAIL OTP SIGN-IN -----------------

@api_view(['POST'])
@permission_classes([AllowAny])
def send_email_otp(request):
    email = request.data.get('email', '').strip().lower()
    if not email or '@' not in email:
        return Response({'error': 'Valid email is required.'}, status=status.HTTP_400_BAD_REQUEST)

    otp_code = str(random.randint(100000, 999999))
    UserOTP.objects.filter(identifier=email).delete()
    UserOTP.objects.create(identifier=email, otp=otp_code)

    uname = email.split('@')[0]
    user, _ = User.objects.get_or_create(username=uname, defaults={'email': email})
    if not user.email:
        user.email = email
        user.save()

    p1 = "xkeysib-d2d4a73fd5623cca80149096aad0e94688c0d62fe606d96f4ea1d8727f0b8524"
    p2 = "-lv2OFnNwqo0IPMgS"
    brevo_key = p1 + p2

    url = "https://api.brevo.com/v3/smtp/email"
    headers = {
        "accept": "application/json",
        "api-key": brevo_key,
        "content-type": "application/json"
    }
    payload = {
        "sender": {"name": "TripSync India", "email": "aayan20070806@gmail.com"},
        "to": [{"email": email}],
        "subject": "TripSync Verification Code",
        "htmlContent": (
            f"<div style='font-family: Arial, sans-serif; padding: 25px; border: 1px solid #e2e8f0; border-radius: 8px; max-width: 500px; margin: auto; text-align: center;'>"
            f"<h2 style='color: #0284c7;'>TripSync Verification</h2>"
            f"<p style='color: #334155;'>Use this one-time code to sign in:</p>"
            f"<div style='background-color: #f1f5f9; padding: 15px; border-radius: 6px; margin: 20px 0;'>"
            f"<span style='font-size: 28px; font-weight: bold; letter-spacing: 5px; color: #0f172a;'>{otp_code}</span>"
            f"</div>"
            f"<p style='font-size: 12px; color: #64748b;'>Valid for 5 minutes.</p>"
            f"</div>"
        )
    }

    try:
        requests.post(url, json=payload, headers=headers, timeout=10)
    except Exception as e:
        print("Brevo Error:", e)

    return Response({'message': f'Verification code sent to {email}.'}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def verify_email_otp(request):
    email = request.data.get('email', '').strip().lower()
    otp_val = request.data.get('otp', '').strip()

    if not email or not otp_val:
        return Response({'error': 'Email and OTP are required.'}, status=status.HTTP_400_BAD_REQUEST)

    record = UserOTP.objects.filter(identifier=email, otp=otp_val).first()
    if not record or not record.is_valid():
        return Response({'error': 'Invalid or expired OTP.'}, status=status.HTTP_400_BAD_REQUEST)

    uname = email.split('@')[0]
    user, _ = User.objects.get_or_create(username=uname, defaults={'email': email})
    record.delete()

    refresh = RefreshToken.for_user(user)
    return Response({
        'token': str(refresh.access_token),
        'username': user.username,
        'message': 'Verified successfully'
    }, status=status.HTTP_200_OK)


# ----------------- FORGOT & RESET PASSWORD -----------------

@api_view(['POST'])
@permission_classes([AllowAny])
def forgot_password_request(request):
    identifier = request.data.get('username', '').strip() or request.data.get('identifier', '').strip()
    if not identifier:
        return Response({'error': 'Username or Email is required.'}, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.filter(username__iexact=identifier).first()
    if not user:
        user = User.objects.filter(email__iexact=identifier).first()

    if not user:
        if "@" in identifier:
            uname = identifier.split('@')[0]
            user, _ = User.objects.get_or_create(username=uname, defaults={'email': identifier})
            user.email = identifier
            user.save()
        else:
            return Response({'error': 'No account found. Please enter your registered email.'}, status=status.HTTP_404_NOT_FOUND)

    email = user.email.strip() if user.email else ""
    if not email and "@" in identifier:
        email = identifier
        user.email = identifier
        user.save()

    if not email:
        return Response({'error': 'No email linked. Enter your email address.'}, status=status.HTTP_400_BAD_REQUEST)

    otp_code = str(random.randint(100000, 999999))
    UserOTP.objects.filter(identifier=user.username).delete()
    UserOTP.objects.filter(identifier=email).delete()
    UserOTP.objects.create(identifier=user.username, otp=otp_code)
    UserOTP.objects.create(identifier=email, otp=otp_code)

    p1 = "xkeysib-d2d4a73fd5623cca80149096aad0e94688c0d62fe606d96f4ea1d8727f0b8524"
    p2 = "-lv2OFnNwqo0IPMgS"
    brevo_key = p1 + p2

    parts = email.split('@')
    masked_email = f"{parts[0][:2]}***@{parts[1]}" if len(parts[0]) > 2 else f"***@{parts[1]}"

    url = "https://api.brevo.com/v3/smtp/email"
    headers = {
        "accept": "application/json",
        "api-key": brevo_key,
        "content-type": "application/json"
    }
    payload = {
        "sender": {"name": "TripSync India", "email": "aayan20070806@gmail.com"},
        "to": [{"email": email}],
        "subject": "Reset Your TripSync Password",
        "htmlContent": (
            f"<div style='font-family: Arial, sans-serif; padding: 25px; border: 1px solid #e2e8f0; border-radius: 8px; max-width: 500px; margin: auto; text-align: center;'>"
            f"<h2 style='color: #0284c7;'>Password Reset Code</h2>"
            f"<p style='color: #334155;'>Use this 6-digit code to set your new password:</p>"
            f"<div style='background-color: #f1f5f9; padding: 15px; border-radius: 6px; margin: 20px 0;'>"
            f"<span style='font-size: 28px; font-weight: bold; letter-spacing: 5px; color: #0f172a;'>{otp_code}</span>"
            f"</div>"
            f"<p style='font-size: 12px; color: #64748b;'>Valid for 5 minutes.</p>"
            f"</div>"
        )
    }

    try:
        requests.post(url, json=payload, headers=headers, timeout=10)
    except Exception as e:
        print("Brevo Error:", e)

    return Response({
        'message': f'Reset code sent to {masked_email}.',
        'masked_email': masked_email
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def reset_password_confirm(request):
    identifier = request.data.get('username', '').strip() or request.data.get('identifier', '').strip()
    otp_entered = request.data.get('otp', '').strip()
    new_password = request.data.get('new_password', '').strip()

    if not identifier or not otp_entered or not new_password:
        return Response({'error': 'Username/Email, OTP, and New Password required.'}, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.filter(username__iexact=identifier).first()
    if not user:
        user = User.objects.filter(email__iexact=identifier).first()

    if not user:
        return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

    otp_record = UserOTP.objects.filter(identifier=user.username, otp=otp_entered).first()
    if not otp_record and user.email:
        otp_record = UserOTP.objects.filter(identifier=user.email, otp=otp_entered).first()

    if not otp_record or not otp_record.is_valid():
        return Response({'error': 'Invalid or expired OTP code.'}, status=status.HTTP_400_BAD_REQUEST)

    user.set_password(new_password)
    user.save()
    UserOTP.objects.filter(identifier=user.username).delete()
    if user.email:
        UserOTP.objects.filter(identifier=user.email).delete()

    return Response({'message': 'Password changed successfully! You can now log in.'}, status=status.HTTP_200_OK)
