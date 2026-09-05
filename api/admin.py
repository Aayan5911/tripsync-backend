from django.contrib import admin
from .models import User, Trip, MemberPreference, Expense, Review

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'phone_number', 'is_staff')

@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = ('destination', 'user', 'total_budget', 'group_size', 'start_date')

@admin.register(MemberPreference)
class MemberPreferenceAdmin(admin.ModelAdmin):
    list_display = ('trip', 'member_name', 'sightseeing_pct', 'food_pct')

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('trip', 'title', 'amount', 'paid_by')

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('trip', 'user', 'rating', 'created_at')