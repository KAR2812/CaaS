"""Subscription and billing models."""
import uuid
from django.db import models
from django.conf import settings


class Plan(models.Model):
    """Subscription plan model."""
    TIER_CHOICES = [
        ('free', 'Free'),
        ('pro', 'Pro'),
        ('team', 'Team'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50)
    tier = models.CharField(max_length=20, choices=TIER_CHOICES, unique=True)
    price_monthly = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Quotas
    tokens_per_month = models.IntegerField()
    scheduled_posts = models.IntegerField(help_text="-1 for unlimited")
    workspaces = models.IntegerField()
    team_members = models.IntegerField()
    
    # Features (JSON field for flexibility)
    features = models.JSONField(default=list)
    
    # Stripe
    stripe_price_id = models.CharField(max_length=255, blank=True)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'plans'
    
    def __str__(self):
        return f"{self.name} (${self.price_monthly}/mo)"


class Subscription(models.Model):
    """Subscription model linking organizations to plans."""
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('canceled', 'Canceled'),
        ('past_due', 'Past Due'),
        ('trialing', 'Trialing'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.OneToOneField(
        'organizations.Organization',
        on_delete=models.CASCADE,
        related_name='subscription'
    )
    plan = models.ForeignKey(Plan, on_delete=models.PROTECT, related_name='subscriptions')
    
    # Stripe fields
    stripe_subscription_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
    stripe_customer_id = models.CharField(max_length=255, null=True, blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Usage tracking
    tokens_used_this_period = models.IntegerField(default=0)
    tokens_remaining = models.IntegerField(default=0)
    
    # Billing cycle
    current_period_start = models.DateTimeField(null=True, blank=True)
    current_period_end = models.DateTimeField(null=True, blank=True)
    cancel_at_period_end = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'subscriptions'
    
    def __str__(self):
        return f"{self.organization.name} - {self.plan.name}"
    
    def has_tokens_available(self, required_tokens):
        """Check if subscription has enough tokens."""
        return self.tokens_remaining >= required_tokens
