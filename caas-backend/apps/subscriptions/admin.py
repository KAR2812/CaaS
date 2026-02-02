"""Admin for subscriptions."""
from django.contrib import admin
from .models import Plan, Subscription


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'tier', 'price_monthly', 'tokens_per_month', 'is_active']
    list_filter = ['tier', 'is_active']


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['organization', 'plan', 'status', 'tokens_remaining', 'current_period_end']
    list_filter = ['status', 'plan']
    search_fields = ['organization__name', 'stripe_subscription_id']
