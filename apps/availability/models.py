from django.db import models
from apps.tours.models import Tour


class TourSchedule(models.Model):
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name='schedules')
    date = models.DateField(db_index=True)
    is_blocked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'tour_schedules'
        unique_together = ['tour', 'date']
        ordering = ['date']

    def __str__(self):
        return f'{self.tour.title} — {self.date}'


class TimeSlot(models.Model):
    schedule = models.ForeignKey(TourSchedule, on_delete=models.CASCADE, related_name='time_slots')
    start_time = models.TimeField()
    end_time = models.TimeField(null=True, blank=True)
    capacity = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'time_slots'
        ordering = ['start_time']

    @property
    def available_spots(self):
        booked = self.bookings.filter(status__in=['pending', 'confirmed']).aggregate(
            total=models.Sum(
                models.F('adult_count') + models.F('child_count') + models.F('infant_count')
            )
        )['total'] or 0
        return max(self.capacity - booked, 0)

    @property
    def is_available(self):
        return self.is_active and not self.schedule.is_blocked and self.available_spots > 0
