from django.contrib import admin
from .models import MembershipPlan, UserMembership, GymClass


@admin.register(MembershipPlan)
class MembershipPlanAdmin(admin.ModelAdmin):
    list_display = ['display_name', 'price', 'billing_cycle', 'duration_days', 'is_active']
    list_filter = ['billing_cycle', 'is_active']


@admin.register(UserMembership)
class UserMembershipAdmin(admin.ModelAdmin):
    list_display = ['user', 'plan', 'start_date', 'end_date', 'status', 'is_active']
    list_filter = ['status', 'is_active', 'plan']
    search_fields = ['user__email']
    date_hierarchy = 'start_date'
    readonly_fields = ['created_at', 'updated_at']


@admin.register(GymClass)
class GymClassAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'trainer', 'duration_minutes', 'max_capacity', 'is_active']
    list_filter = ['category', 'is_active']
    search_fields = ['name']
