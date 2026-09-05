from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from django.contrib.auth import get_user_model

from .models import Trip, MemberPreference, Expense, Review
from .serializers import (
    UserRegisterSerializer, TripSerializer, 
    MemberPreferenceSerializer, ExpenseSerializer, ReviewSerializer
)
from .utils import generate_trip_breakdown

User = get_user_model()

@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    username = request.data.get('username')
    password = request.data.get('password')
    email = request.data.get('email', '')
    phone_number = request.data.get('phone_number', '')

    if not username or not password:
        return Response({'detail': 'Username and password required'}, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(username=username).exists():
        return Response({'detail': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.create_user(username=username, password=password, email=email)
    if hasattr(user, 'phone_number'):
        user.phone_number = phone_number
    user.save()

    return Response({
        'message': 'User registered successfully',
        'username': user.username
    }, status=status.HTTP_201_CREATED)


class RegisterView(generics.CreateAPIView):
    serializer_class = UserRegisterSerializer
    permission_classes = [permissions.AllowAny]


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
    import random
from django.core.mail import send_mail
from django.contrib.auth.models import User
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from .models import UserOTP

@api_view(['POST'])
@permission_classes([AllowAny])
def send_email_otp(request):
    email = request.data.get('email', '').strip()
    if not email:
        return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    user = User.objects.filter(email__iexact=email).first()
    if not user:
        return Response({'error': 'No account found with this email. Please register first.'}, status=status.HTTP_404_NOT_FOUND)
    
    otp_code = str(random.randint(100000, 999999))
    UserOTP.objects.filter(identifier=email).delete()
    UserOTP.objects.create(identifier=email, otp=otp_code)
    
    try:
        send_mail(
            subject='TripSync Login OTP',
            message=f'Hello {user.username},\n\nYour OTP is: {otp_code}\nValid for 5 mins.',
            from_email=None,
            recipient_list=[email],
            fail_silently=False,
        )
        return Response({'message': 'OTP sent to registered email.'})
    except Exception as e:
        return Response({'error': f'Failed to send email: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
        'username': user.username,
        'email': user.email
    })

@api_view(['POST'])
@permission_classes([AllowAny])
def send_phone_otp(request):
    phone = request.data.get('phone', '').strip()
    if not phone:
        return Response({'error': 'Phone number is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    otp_code = str(random.randint(100000, 999999))
    UserOTP.objects.filter(identifier=phone).delete()
    UserOTP.objects.create(identifier=phone, otp=otp_code)
    
    return Response({'message': f'OTP generated successfully! (Testing OTP: {otp_code})'})

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