import django_filters
from .models import Tour


class TourFilter(django_filters.FilterSet):
    min_price = django_filters.NumberFilter(field_name='price_adult', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='price_adult', lookup_expr='lte')
    destination = django_filters.CharFilter(field_name='destination__slug')
    duration_days = django_filters.NumberFilter()
    min_duration = django_filters.NumberFilter(field_name='duration_days', lookup_expr='gte')
    max_duration = django_filters.NumberFilter(field_name='duration_days', lookup_expr='lte')

    class Meta:
        model = Tour
        fields = ['destination', 'is_featured', 'currency', 'min_price', 'max_price', 'duration_days']
