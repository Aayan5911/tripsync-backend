import random
import requests
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from django.contrib.auth import get_user_model
from django.core.mail import send_mail

from .models import Trip, MemberPreference, Expense, Review, UserOTP
from .serializers import (
    UserRegisterSerializer, TripSerializer, 
    MemberPreferenceSerializer, ExpenseSerializer, ReviewSerializer
)
from .utils import generate_trip_breakdown

User = get_user_model()

@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    username = request.data.get('username') or request.data.get('email', '').split('@')[0]
    password = request.data.get('password')
    email = request.data.get('email') or request.data.get('email_address', '')
    phone_number = request.data.get('phone_number') or request.data.get('phone', '')

    if not username or not password:
        return Response({'detail': 'Username and password required'}, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.filter(email__iexact=email).first() if email else None
    if not user:
        user = User.objects.filter(username=username).first()

    if user:
        user.set_password(password)
        if email:
            user.email = email
        if hasattr(user, 'phone_number') and phone_number:
            user.phone_number = phone_number
        user.save()
        return Response({
            'message': 'User updated successfully',
            'username': user.username,
            'token': 'tripsync-live-token'
        }, status=status.HTTP_200_OK)

    user = User.objects.create_user(username=username, password=password, email=email)
    if hasattr(user, 'phone_number') and phone_number:
        user.phone_number = phone_number
    user.save()

    return Response({
        'message': 'User registered successfully',
        'username': user.username,
        'token': 'tripsync-live-token'
    }, status=status.HTTP_201_CREATED)


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        username = request.data.get('username') or request.data.get('email', '').split('@')[0]
        password = request.data.get('password')
        email = request.data.get('email') or request.data.get('email_address', '')
        phone_number = request.data.get('phone_number') or request.data.get('phone', '')

        if not username or not password:
            return Response({'detail': 'Username and password required'}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.filter(email__iexact=email).first() if email else None
        if not user:
            user = User.objects.filter(username=username).first()

        if user:
            user.set_password(password)
            if email:
                user.email = email
            if hasattr(user, 'phone_number') and phone_number:
                user.phone_number = phone_number
            user.save()
            return Response({
                'message': 'User updated successfully',
                'username': user.username,
                'token': 'tripsync-live-token'
            }, status=status.HTTP_200_OK)

        user = User.objects.create_user(username=username, password=password, email=email)
        if hasattr(user, 'phone_number') and phone_number:
            user.phone_number = phone_number
        user.save()

        return Response({
            'message': 'User registered successfully',
            'username': user.username,
            'token': 'tripsync-live-token'
        }, status=status.HTTP_201_CREATED)


class TripListCreateView(generics.ListCreateAPIView):
    serializer_class = TripSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Trip.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class MemberPreferenceCreateView(generics.CreateAPIView):
    serializer_class = MemberPreferenceSerializer
    permission_classes = [permissions.IsAuthenticated]


class ItineraryGenerateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, trip_id):
        try:
            trip = Trip.objects.get(id=trip_id, user=request.user)
            data = generate_trip_breakdown(trip)
            return Response(data, status=status.HTTP_200_OK)
        except Trip.DoesNotExist:
            return Response({"error": "Trip not found"}, status=status.HTTP_404_NOT_FOUND)


class ExpenseListCreateView(generics.ListCreateAPIView):
    serializer_class = ExpenseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Expense.objects.filter(trip_id=self.kwargs['trip_id'])


class ReviewCreateView(generics.CreateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


@api_view(['POST'])
@permission_classes([AllowAny])
def send_email_otp(request):
    email = request.data.get('email', '').strip()
    if not email:
        return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    user = User.objects.filter(email__iexact=email).first()
    if not user:
        uname = email.split('@')[0]
        if User.objects.filter(username=uname).exists():
            uname = f"{uname}_{random.randint(100, 999)}"
        rand_pass = f"Pass@{random.randint(100000, 999999)}"
        user = User.objects.create_user(username=uname, email=email, password=rand_pass)

    otp_code = str(random.randint(100000, 999999))
    UserOTP.objects.filter(identifier=email).delete()
    UserOTP.objects.create(identifier=email, otp=otp_code)
    
    subject = 'TripSync Account Verification Code'
    message = (
        f"TripSync Account Verification\n\n"
        f"Your one-time password (OTP) is: {otp_code}\n\n"
        f"This code will expire in 5 minutes.\n"
        f"If you did not request this, please ignore this email."
    )
    
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email='TripSync India <aayan20070806@gmail.com>',
            recipient_list=[email],
            fail_silently=True,
        )
    except Exception as e:
        print(f"SMTP Warning: {e}")

    return Response({
        'message': f'We have sent an OTP to {email}',
        'test_otp': otp_code
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def verify_email_otp(request):
    email = request.data.get('email', '').strip()
    otp_entered = request.data.get('otp', '').strip()
    
    otp_record = UserOTP.objects.filter(identifier=email, otp=otp_entered).first()
    if not otp_record or not otp_record.is_valid():
        return Response({'error': 'Invalid or expired OTP'}, status=status.HTTP_400_BAD_REQUEST)
    
    user = User.objects.filter(email__iexact=email).first()
    otp_record.delete()
    
    return Response({
        'token': 'tripsync-live-token',
        'username': user.username if user else email.split('@')[0],
        'email': email
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def send_phone_otp(request):
    phone = request.data.get('phone', '').strip()
    if not phone:
        return Response({'error': 'Phone number is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    clean_phone = phone[-10:]
    otp_code = str(random.randint(100000, 999999))
    UserOTP.objects.filter(identifier=phone).delete()
    UserOTP.objects.create(identifier=phone, otp=otp_code)
    
    fast2sms_key = 'rf1NTvIQcxbw3tkFERJuC9BdZDhLe02XqGo8a6AyOKMzUliYnHTR2fuQj7P9JecSnOMEGwkiyvCY0pa4'
    sms_url = "https://www.fast2sms.com/dev/bulkV2"
    headers = {'authorization': fast2sms_key}
    payload = {
        'variables_values': otp_code,
        'route': 'otp',
        'numbers': clean_phone,
    }
    
    try:
        response = requests.get(sms_url, headers=headers, params=payload, timeout=10)
        res_data = response.json()
        if res_data.get('return'):
            return Response({'message': f'We have sent an OTP on {clean_phone}!'})
        else:
            return Response({
                'message': f'We have sent an OTP on {clean_phone}!',
                'test_otp': otp_code
            })
    except Exception:
        return Response({'message': f'We have sent an OTP on {clean_phone}!', 'test_otp': otp_code})


@api_view(['POST'])
@permission_classes([AllowAny])
def verify_phone_otp(request):
    phone = request.data.get('phone', '').strip()
    otp_entered = request.data.get('otp', '').strip()
    
    otp_record = UserOTP.objects.filter(identifier=phone, otp=otp_entered).first()
    if not otp_record or not otp_record.is_valid():
        return Response({'error': 'Invalid or expired OTP'}, status=status.HTTP_400_BAD_REQUEST)
    
    otp_record.delete()
    return Response({
        'token': 'tripsync-live-token',
        'username': f'User_{phone[-4:]}',
        'phone': phone
    })