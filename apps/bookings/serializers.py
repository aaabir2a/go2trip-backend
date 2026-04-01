from rest_framework import serializers
from apps.tours.serializers import TourListSerializer
from apps.availability.models import TimeSlot
from .models import Booking


class BookingCreateSerializer(serializers.ModelSerializer):
    # Guest fields — required when not authenticated
    guest_name = serializers.CharField(required=False, allow_blank=True)
    guest_email = serializers.EmailField(required=False, allow_blank=True)
    guest_phone = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Booking
        fields = [
            'tour', 'time_slot', 'adult_count', 'child_count',
            'infant_count', 'special_requests',
            'guest_name', 'guest_email', 'guest_phone',
        ]

    def validate(self, attrs):
        request = self.context.get('request')
        is_guest = not (request and request.user and request.user.is_authenticated)

        if is_guest:
            if not attrs.get('guest_name', '').strip():
                raise serializers.ValidationError({'guest_name': 'Name is required.'})
            if not attrs.get('guest_email', '').strip():
                raise serializers.ValidationError({'guest_email': 'Email is required.'})
            if not attrs.get('guest_phone', '').strip():
                raise serializers.ValidationError({'guest_phone': 'Phone is required.'})

        slot = attrs['time_slot']
        if slot.schedule.tour != attrs['tour']:
            raise serializers.ValidationError('Time slot does not belong to this tour.')
        if not slot.is_available:
            raise serializers.ValidationError('This time slot is not available.')
        total_people = attrs['adult_count'] + attrs.get('child_count', 0) + attrs.get('infant_count', 0)
        if total_people > slot.available_spots:
            raise serializers.ValidationError(f'Only {slot.available_spots} spots available.')
        return attrs

    def create(self, validated_data):
        from apps.authentication.models import User
        request = self.context.get('request')
        tour = validated_data['tour']
        booking = Booking(**validated_data)
        if request and request.user and request.user.is_authenticated:
            booking.user = request.user
        else:
            # Auto-create a customer account from guest info
            guest_email = validated_data.get('guest_email', '').strip()
            guest_name  = validated_data.get('guest_name', '').strip()
            guest_phone = validated_data.get('guest_phone', '').strip()
            if guest_email:
                parts = guest_name.split(None, 1)
                first = parts[0] if parts else guest_name
                last  = parts[1] if len(parts) > 1 else ''
                user, created = User.objects.get_or_create(
                    email=guest_email,
                    defaults={
                        'first_name': first,
                        'last_name':  last,
                        'phone':      guest_phone,
                        'role':       'customer',
                    }
                )
                if created:
                    user.set_password(guest_name)   # password = full name
                    user.save()
                booking.user = user
        booking.currency = tour.currency
        booking.total_price = booking.calculate_total()
        booking.save()
        return booking


class BookingSerializer(serializers.ModelSerializer):
    tour = TourListSerializer(read_only=True)
    reference = serializers.UUIDField(read_only=True)
    total_people = serializers.ReadOnlyField()
    contact_name = serializers.ReadOnlyField()
    contact_email = serializers.ReadOnlyField()

    class Meta:
        model = Booking
        fields = [
            'id', 'reference', 'tour', 'time_slot',
            'adult_count', 'child_count', 'infant_count', 'total_people',
            'total_price', 'currency', 'status', 'payment_status',
            'guest_name', 'guest_email', 'guest_phone',
            'contact_name', 'contact_email',
            'special_requests', 'cancellation_reason', 'refund_amount',
            'created_at', 'updated_at',
        ]


class BookingStatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=['pending', 'confirmed', 'cancelled', 'completed'])
    cancellation_reason = serializers.CharField(required=False, allow_blank=True)
    payment_status = serializers.ChoiceField(
        choices=['unpaid', 'paid', 'refunded', 'partial_refund'], required=False
    )
