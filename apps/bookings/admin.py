from django.contrib import admin
from .models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['reference', 'user', 'tour', 'total_price', 'status', 'payment_status', 'created_at']
    list_filter = ['status', 'payment_status']
    search_fields = ['user__email', 'tour__title', 'reference']
    readonly_fields = ['reference', 'total_price', 'created_at']
