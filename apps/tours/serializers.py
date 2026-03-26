import json
from rest_framework import serializers
from apps.destinations.models import Destination
from apps.destinations.serializers import DestinationSerializer
from .models import Tour, TourImage, Itinerary, CancellationPolicy


class TourImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = TourImage
        fields = ['id', 'image', 'caption', 'order']


class ItinerarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Itinerary
        fields = ['id', 'day', 'title', 'description', 'image']


class CancellationPolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = CancellationPolicy
        fields = ['free_cancellation_hours', 'partial_refund_percent', 'partial_refund_hours', 'description']


class TourListSerializer(serializers.ModelSerializer):
    destination_name = serializers.CharField(source='destination.name', read_only=True)
    average_rating = serializers.ReadOnlyField()
    review_count = serializers.ReadOnlyField()

    class Meta:
        model = Tour
        fields = [
            'id', 'title', 'slug', 'destination', 'destination_name',
            'duration_days', 'duration_hours', 'max_group_size',
            'price_adult', 'price_child', 'price_infant', 'currency',
            'thumbnail', 'is_featured', 'average_rating', 'review_count',
        ]


class TourDetailSerializer(serializers.ModelSerializer):
    # Read: nested destination object
    destination_detail = DestinationSerializer(source='destination', read_only=True)
    # Write: accept destination PK as 'destination'
    destination = serializers.PrimaryKeyRelatedField(queryset=Destination.objects.all())

    images = TourImageSerializer(many=True, read_only=True)
    itinerary = ItinerarySerializer(many=True, read_only=True)
    cancellation_policy = CancellationPolicySerializer(read_only=True)
    average_rating = serializers.ReadOnlyField()
    review_count = serializers.ReadOnlyField()

    class Meta:
        model = Tour
        fields = [
            'id', 'title', 'slug', 'description',
            'destination', 'destination_detail',
            'duration_days', 'duration_hours', 'max_group_size', 'languages',
            'highlights', 'included', 'excluded',
            'price_adult', 'price_child', 'price_infant', 'currency',
            'thumbnail', 'images', 'itinerary', 'cancellation_policy',
            'booking_cutoff_days', 'is_active', 'is_featured', 'average_rating', 'review_count',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']

    def to_internal_value(self, data):
        # multipart QueryDict sends JSON arrays as plain strings — convert to plain dict first
        mutable = {k: data[k] for k in data} if hasattr(data, 'getlist') else dict(data)
        for field in ('highlights', 'included', 'excluded'):
            val = mutable.get(field)
            if isinstance(val, str):
                try:
                    mutable[field] = json.loads(val)
                except (json.JSONDecodeError, TypeError):
                    mutable[field] = []
        return super().to_internal_value(mutable)
