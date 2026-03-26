from rest_framework import serializers
from apps.authentication.serializers import UserSerializer
from .models import Review


class ReviewSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'user', 'tour', 'rating', 'comment', 'is_approved', 'created_at']
        read_only_fields = ['id', 'user', 'is_approved', 'created_at']


class ReviewCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['tour', 'rating', 'comment']

    def validate(self, attrs):
        user = self.context['request'].user
        tour = attrs['tour']
        # Only users who booked can review
        from apps.bookings.models import Booking
        has_booking = Booking.objects.filter(
            user=user, tour=tour, status__in=['confirmed', 'completed']
        ).exists()
        if not has_booking:
            raise serializers.ValidationError('You must book this tour before reviewing it.')
        if Review.objects.filter(user=user, tour=tour).exists():
            raise serializers.ValidationError('You have already reviewed this tour.')
        return attrs

    def create(self, validated_data):
        return Review.objects.create(user=self.context['request'].user, **validated_data)
