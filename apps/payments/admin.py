from django.contrib import admin
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['user', 'amount', 'currency', 'status', 'payment_type', 'created_at']
    list_filter = ['status', 'payment_type', 'currency']
    search_fields = ['user__email', 'stripe_payment_intent_id']
    readonly_fields = ['stripe_payment_intent_id', 'stripe_charge_id', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'
