from django.contrib import admin
from .models import Destination


@admin.register(Destination)
class DestinationAdmin(admin.ModelAdmin):
    list_display = ['name', 'country', 'location', 'is_active', 'created_at']
    list_filter = ['country', 'is_active']
    search_fields = ['name', 'country']
    prepopulated_fields = {'slug': ('name',)}
