"""Subscription serializers."""
from rest_framework import serializers
from .models import Plan, Subscription


class PlanSerializer(serializers.ModelSerializer):
    """Serializer for subscription plans."""
    
    class Meta:
        model = Plan
        fields = ['id', 'name', 'tier', 'price_monthly', 'tokens_per_month', 
                  'scheduled_posts', 'workspaces', 'team_members', 'features']


class SubscriptionSerializer(serializers.ModelSerializer):
    """Serializer for subscriptions."""
    plan_details = PlanSerializer(source='plan', read_only=True)
    
    class Meta:
        model = Subscription
        fields = ['id', 'organization', 'plan', 'plan_details', 'status', 
                  'tokens_used_this_period', 'tokens_remaining', 
                  'current_period_end', 'cancel_at_period_end']
        read_only_fields = ['id', 'status', 'tokens_used_this_period', 'tokens_remaining']
