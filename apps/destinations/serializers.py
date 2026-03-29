from rest_framework import serializers
from .models import Destination


class DestinationSerializer(serializers.ModelSerializer):
    tour_count = serializers.SerializerMethodField()

    class Meta:
        model = Destination
        fields = ['id', 'name', 'slug', 'description', 'country', 'location', 'thumbnail', 'tour_count', 'is_active', 'is_featured', 'created_at']
        read_only_fields = ['id', 'slug', 'created_at']

    def get_tour_count(self, obj):
        return obj.tours.filter(is_active=True).count()
