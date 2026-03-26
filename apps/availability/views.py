from datetime import date as today_date, timedelta
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from utils.permissions import IsAdmin
from utils.responses import success_response, error_response
from apps.tours.models import Tour
from .models import TourSchedule, TimeSlot
from .serializers import TourScheduleSerializer, TimeSlotSerializer, BlockDateSerializer


class TourAvailabilityView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, slug):
        try:
            tour = Tour.objects.get(slug=slug, is_active=True)
        except Tour.DoesNotExist:
            return error_response('Tour not found.', status_code=404)

        # Hide dates within booking_cutoff_days from today
        cutoff_date = today_date.today() + timedelta(days=tour.booking_cutoff_days)
        qs = tour.schedules.filter(
            date__gte=cutoff_date,
            is_blocked=False
        ).prefetch_related('time_slots')

        year = request.query_params.get('year')
        month = request.query_params.get('month')
        if year and month:
            qs = qs.filter(date__year=year, date__month=month)

        serializer = TourScheduleSerializer(qs, many=True)
        return success_response(data=serializer.data)


class ScheduleManageViewSet(viewsets.ModelViewSet):
    """Admin: manage tour schedules and time slots."""
    serializer_class = TourScheduleSerializer
    permission_classes = [IsAdmin]

    def get_queryset(self):
        qs = TourSchedule.objects.prefetch_related('time_slots').all()
        tour_id = self.request.query_params.get('tour')
        if tour_id:
            qs = qs.filter(tour_id=tour_id)
        return qs

    @action(detail=True, methods=['post'], url_path='time-slots')
    def add_time_slot(self, request, pk=None):
        schedule = self.get_object()
        serializer = TimeSlotSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(schedule=schedule)
        return success_response(data=serializer.data, message='Time slot added.')

    @action(detail=False, methods=['post'], url_path='block-date')
    def block_date(self, request):
        serializer = BlockDateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        tour_id = request.data.get('tour_id')
        schedule, _ = TourSchedule.objects.get_or_create(tour_id=tour_id, date=serializer.validated_data['date'])
        schedule.is_blocked = serializer.validated_data['is_blocked']
        schedule.save()
        return success_response(message=f"Date {'blocked' if schedule.is_blocked else 'unblocked'}.")
