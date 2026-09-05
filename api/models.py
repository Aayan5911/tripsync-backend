from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    phone_number = models.CharField(max_length=15, unique=True, null=True, blank=True)
    emergency_contact = models.CharField(max_length=15, null=True, blank=True)

class Trip(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='trips')
    origin = models.CharField(max_length=100)
    destination = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    total_budget = models.DecimalField(max_digits=10, decimal_places=2)
    group_size = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

class MemberPreference(models.Model):
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name='preferences')
    member_name = models.CharField(max_length=50)
    sightseeing_pct = models.PositiveIntegerField(default=25)
    food_pct = models.PositiveIntegerField(default=25)
    relax_pct = models.PositiveIntegerField(default=25)
    street_explore_pct = models.PositiveIntegerField(default=25)

class Expense(models.Model):
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name='expenses')
    title = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid_by = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

class Review(models.Model):
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField()
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True) 
    import random
from django.db import models
from django.utils import timezone
from datetime import timedelta

class UserOTP(models.Model):
    identifier = models.CharField(max_length=100)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_valid(self):
        return timezone.now() < self.created_at + timedelta(minutes=5)