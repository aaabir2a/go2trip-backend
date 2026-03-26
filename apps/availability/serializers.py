from rest_framework import serializers
from .models import TourSchedule, TimeSlot


class TimeSlotSerializer(serializers.ModelSerializer):
    available_spots = serializers.ReadOnlyField()
    is_available = serializers.ReadOnlyField()

    class Meta:
        model = TimeSlot
        fields = ['id', 'start_time', 'end_time', 'capacity', 'available_spots', 'is_available', 'is_active']


class TourScheduleSerializer(serializers.ModelSerializer):
    time_slots = TimeSlotSerializer(many=True, read_only=True)

    class Meta:
        model = TourSchedule
        fields = ['id', 'tour', 'date', 'is_blocked', 'time_slots']
        read_only_fields = ['id']


class BlockDateSerializer(serializers.Serializer):
    date = serializers.DateField()
    is_blocked = serializers.BooleanField(default=True)
