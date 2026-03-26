import uuid
from django.db import models
from apps.authentication.models import User
from apps.tours.models import Tour
from apps.availability.models import TimeSlot


class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]
    PAYMENT_STATUS_CHOICES = [
        ('unpaid', 'Unpaid'),
        ('paid', 'Paid'),
        ('refunded', 'Refunded'),
        ('partial_refund', 'Partial Refund'),
    ]

    reference = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name='bookings')
    tour = models.ForeignKey(Tour, on_delete=models.PROTECT, related_name='bookings')
    time_slot = models.ForeignKey(TimeSlot, on_delete=models.PROTECT, related_name='bookings')
    adult_count = models.PositiveIntegerField(default=1)
    child_count = models.PositiveIntegerField(default=0)
    infant_count = models.PositiveIntegerField(default=0)
    total_price = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default='BDT')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='unpaid')
    special_requests = models.TextField(blank=True)
    cancellation_reason = models.TextField(blank=True)
    refund_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'bookings'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['tour', 'status']),
        ]

    def __str__(self):
        return f'Booking #{self.reference} — {self.tour.title}'

    def calculate_total(self):
        tour = self.tour
        total = (
            tour.price_adult * self.adult_count +
            tour.price_child * self.child_count +
            tour.price_infant * self.infant_count
        )
        return total

    @property
    def total_people(self):
        return self.adult_count + self.child_count + self.infant_count
