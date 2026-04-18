from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, TrainerProfile, ProgressEntry


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ['email', 'get_full_name', 'is_trainer', 'is_active', 'created_at']
    list_filter = ['is_trainer', 'is_active', 'fitness_goal', 'fitness_level']
    search_fields = ['email', 'first_name', 'last_name']
    ordering = ['-created_at']

    fieldsets = UserAdmin.fieldsets + (
        ('Fitness Profile', {
            'fields': (
                'phone', 'date_of_birth', 'gender', 'profile_image',
                'height_cm', 'weight_kg', 'fitness_goal', 'fitness_level',
                'is_trainer', 'bio'
            )
        }),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Profile', {
            'fields': ('email', 'first_name', 'last_name', 'is_trainer')
        }),
    )


@admin.register(TrainerProfile)
class TrainerProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'specialization', 'years_experience', 'hourly_rate', 'is_available', 'rating']
    list_filter = ['specialization', 'is_available']
    search_fields = ['user__email', 'user__first_name', 'user__last_name']


@admin.register(ProgressEntry)
class ProgressEntryAdmin(admin.ModelAdmin):
    list_display = ['user', 'date', 'weight_kg', 'body_fat_percentage']
    list_filter = ['date']
    search_fields = ['user__email']
    date_hierarchy = 'date'
