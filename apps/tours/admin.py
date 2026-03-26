from django.contrib import admin
from .models import Tour, TourImage, Itinerary, CancellationPolicy


class TourImageInline(admin.TabularInline):
    model = TourImage
    extra = 1


class ItineraryInline(admin.TabularInline):
    model = Itinerary
    extra = 1


@admin.register(Tour)
class TourAdmin(admin.ModelAdmin):
    list_display = ['title', 'destination', 'price_adult', 'currency', 'is_active', 'is_featured', 'created_at']
    list_filter = ['destination', 'is_active', 'is_featured', 'currency']
    search_fields = ['title', 'description']
    prepopulated_fields = {'slug': ('title',)}
    inlines = [TourImageInline, ItineraryInline]


admin.site.register(CancellationPolicy)
