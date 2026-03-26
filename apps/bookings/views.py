import logging
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from utils.permissions import IsAdmin, IsOwnerOrAdmin
from utils.responses import success_response, created_response, error_response
from .models import Booking
from .serializers import BookingSerializer, BookingCreateSerializer, BookingStatusUpdateSerializer

logger = logging.getLogger('apps')


class BookingViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return BookingCreateSerializer
        return BookingSerializer

    def get_queryset(self):
        user = self.request.user
        qs = Booking.objects.select_related('tour', 'tour__destination', 'time_slot')
        if user.role == 'admin':
            return qs
        return qs.filter(user=user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        booking = serializer.save()
        logger.info(f'New booking {booking.reference} by {request.user.email}')
        return created_response(
            data=BookingSerializer(booking).data,
            message='Booking created successfully.',
        )

    @action(detail=True, methods=['post'], url_path='update-status', permission_classes=[IsAdmin])
    def update_status(self, request, pk=None):
        booking = self.get_object()
        serializer = BookingStatusUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        booking.status = data['status']
        if 'payment_status' in data:
            booking.payment_status = data['payment_status']
        if data['status'] == 'cancelled':
            booking.cancellation_reason = data.get('cancellation_reason', '')
            booking = self._apply_cancellation_policy(booking)
        booking.save()
        return success_response(data=BookingSerializer(booking).data, message='Booking updated.')

    @action(detail=True, methods=['post'], url_path='cancel')
    def cancel(self, request, pk=None):
        booking = self.get_object()
        if booking.user != request.user and request.user.role != 'admin':
            return error_response('Not authorised.', status_code=403)
        if booking.status in ['cancelled', 'completed']:
            return error_response('Cannot cancel this booking.')
        booking.status = 'cancelled'
        booking.cancellation_reason = request.data.get('reason', '')
        booking = self._apply_cancellation_policy(booking)
        booking.save()
        return success_response(data=BookingSerializer(booking).data, message='Booking cancelled.')

    def _apply_cancellation_policy(self, booking):
        try:
            policy = booking.tour.cancellation_policy
            from django.utils import timezone
            slot = booking.time_slot
            tour_datetime = timezone.make_aware(
                __import__('datetime').datetime.combine(slot.schedule.date, slot.start_time)
            )
            hours_until = (tour_datetime - timezone.now()).total_seconds() / 3600
            if hours_until >= policy.free_cancellation_hours:
                booking.refund_amount = booking.total_price
                booking.payment_status = 'refunded'
            elif hours_until >= policy.partial_refund_hours:
                booking.refund_amount = booking.total_price * policy.partial_refund_percent / 100
                booking.payment_status = 'partial_refund'
        except Exception:
            pass
        return booking
