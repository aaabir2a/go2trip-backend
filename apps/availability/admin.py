from django.contrib import admin
from .models import TourSchedule, TimeSlot


class TimeSlotInline(admin.TabularInline):
    model = TimeSlot
    extra = 1


@admin.register(TourSchedule)
class TourScheduleAdmin(admin.ModelAdmin):
    list_display = ['tour', 'date', 'is_blocked']
    list_filter = ['is_blocked', 'date']
    search_fields = ['tour__title']
    inlines = [TimeSlotInline]
