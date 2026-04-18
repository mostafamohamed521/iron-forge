from django.contrib import admin
from .models import TrainingSession, Booking


@admin.register(TrainingSession)
class TrainingSessionAdmin(admin.ModelAdmin):
    list_display = ['title', 'trainer', 'date', 'start_time', 'session_type', 'current_participants', 'max_participants', 'status']
    list_filter = ['session_type', 'status', 'date']
    search_fields = ['title', 'trainer__email']
    date_hierarchy = 'date'


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['user', 'session', 'status', 'rating', 'created_at']
    list_filter = ['status']
    search_fields = ['user__email']
    readonly_fields = ['created_at', 'updated_at']
