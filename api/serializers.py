from rest_framework import serializers
from .models import User, Trip, MemberPreference, Expense, Review

class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'phone_number', 'emergency_contact', 'password']

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

class MemberPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = MemberPreference
        fields = '__all__'

class TripSerializer(serializers.ModelSerializer):
    preferences = MemberPreferenceSerializer(many=True, read_only=True)

    class Meta:
        model = Trip
        fields = '__all__'
        read_only_fields = ['user']

class ExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expense
        fields = '__all__'

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = '__all__'
        read_only_fields = ['user']