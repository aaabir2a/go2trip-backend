from rest_framework import serializers
from apps.tours.serializers import TourListSerializer
from apps.availability.models import TimeSlot
from .models import Booking


class BookingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = [
            'tour', 'time_slot', 'adult_count', 'child_count',
            'infant_count', 'special_requests',
        ]

    def validate(self, attrs):
        slot = attrs['time_slot']
        # Ensure slot belongs to the tour
        if slot.schedule.tour != attrs['tour']:
            raise serializers.ValidationError('Time slot does not belong to this tour.')
        if not slot.is_available:
            raise serializers.ValidationError('This time slot is not available.')
        total_people = attrs['adult_count'] + attrs.get('child_count', 0) + attrs.get('infant_count', 0)
        if total_people > slot.available_spots:
            raise serializers.ValidationError(f'Only {slot.available_spots} spots available.')
        return attrs

    def create(self, validated_data):
        tour = validated_data['tour']
        booking = Booking(**validated_data)
        booking.user = self.context['request'].user
        booking.currency = tour.currency
        booking.total_price = booking.calculate_total()
        booking.save()
        return booking


class BookingSerializer(serializers.ModelSerializer):
    tour = TourListSerializer(read_only=True)
    reference = serializers.UUIDField(read_only=True)
    total_people = serializers.ReadOnlyField()

    class Meta:
        model = Booking
        fields = [
            'id', 'reference', 'tour', 'time_slot',
            'adult_count', 'child_count', 'infant_count', 'total_people',
            'total_price', 'currency', 'status', 'payment_status',
            'special_requests', 'cancellation_reason', 'refund_amount',
            'created_at', 'updated_at',
        ]


class BookingStatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=['pending', 'confirmed', 'cancelled', 'completed'])
    cancellation_reason = serializers.CharField(required=False, allow_blank=True)
    payment_status = serializers.ChoiceField(
        choices=['unpaid', 'paid', 'refunded', 'partial_refund'], required=False
    )
