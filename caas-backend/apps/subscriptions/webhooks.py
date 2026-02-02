"""
Stripe webhook handlers.
"""
import logging
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.views.decorators.http import require_POST
from django.utils import timezone

from .models import Subscription, Plan
from .stripe_service import StripeService
from apps.organizations.models import Organization

logger = logging.getLogger(__name__)


@csrf_exempt
@require_POST
def stripe_webhook(request):
    """
    Handle Stripe webhooks.
    POST /api/v1/subscriptions/webhook/
    """
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    
    # Verify webhook signature
    result = StripeService.verify_webhook_signature(payload, sig_header)
    if not result['success']:
        logger.warning(f"Webhook verification failed: {result['error']}")
        return HttpResponse(status=400)
    
    event = result['event']
    event_type = event['type']
    
    logger.info(f"Processing Stripe webhook: {event_type}")
    
    try:
        if event_type == 'checkout.session.completed':
            handle_checkout_completed(event['data']['object'])
        
        elif event_type == 'customer.subscription.created':
            handle_subscription_created(event['data']['object'])
        
        elif event_type == 'customer.subscription.updated':
            handle_subscription_updated(event['data']['object'])
        
        elif event_type == 'customer.subscription.deleted':
            handle_subscription_deleted(event['data']['object'])
        
        elif event_type == 'invoice.payment_succeeded':
            handle_payment_succeeded(event['data']['object'])
        
        elif event_type == 'invoice.payment_failed':
            handle_payment_failed(event['data']['object'])
        
        return HttpResponse(status=200)
    
    except Exception as e:
        logger.error(f"Webhook processing error: {e}")
        return HttpResponse(status=500)


def handle_checkout_completed(session):
    """Handle successful checkout."""
    org_id = session['metadata'].get('organization_id')
    subscription_id = session['subscription']
    customer_id = session['customer']
    
    logger.info(f"Checkout completed for org {org_id}, subscription {subscription_id}")


def handle_subscription_created(stripe_subscription):
    """Handle subscription creation."""
    subscription_id = stripe_subscription['id']
    customer_id = stripe_subscription['customer']
    status = stripe_subscription['status']
    
    # Find subscription in our DB and update
    try:
        subscription = Subscription.objects.get(stripe_subscription_id=subscription_id)
        subscription.status = status
        subscription.current_period_start = timezone.datetime.fromtimestamp(
            stripe_subscription['current_period_start'], tz=timezone.utc
        )
        subscription.current_period_end = timezone.datetime.fromtimestamp(
            stripe_subscription['current_period_end'], tz=timezone.utc
        )
        subscription.tokens_remaining = subscription.plan.tokens_per_month
        subscription.save()
        
        logger.info(f"Subscription {subscription_id} created successfully")
    except Subscription.DoesNotExist:
        logger.warning(f"Subscription {subscription_id} not found in database")


def handle_subscription_updated(stripe_subscription):
    """Handle subscription updates."""
    subscription_id = stripe_subscription['id']
    status = stripe_subscription['status']
    
    try:
        subscription = Subscription.objects.get(stripe_subscription_id=subscription_id)
        subscription.status = status
        subscription.cancel_at_period_end = stripe_subscription.get('cancel_at_period_end', False)
        subscription.save()
        
        logger.info(f"Subscription {subscription_id} updated")
    except Subscription.DoesNotExist:
        logger.warning(f"Subscription {subscription_id} not found")


def handle_subscription_deleted(stripe_subscription):
    """Handle subscription cancellation."""
    subscription_id = stripe_subscription['id']
    
    try:
        subscription = Subscription.objects.get(stripe_subscription_id=subscription_id)
        subscription.status = 'canceled'
        subscription.save()
        
        logger.info(f"Subscription {subscription_id} canceled")
    except Subscription.DoesNotExist:
        logger.warning(f"Subscription {subscription_id} not found")


def handle_payment_succeeded(invoice):
    """Handle successful payment - reset token quota."""
    subscription_id = invoice.get('subscription')
    
    if subscription_id:
        try:
            subscription = Subscription.objects.get(stripe_subscription_id=subscription_id)
            # Reset tokens for new period
            subscription.tokens_used_this_period = 0
            subscription.tokens_remaining = subscription.plan.tokens_per_month
            subscription.save()
            
            logger.info(f"Payment succeeded, tokens reset for subscription {subscription_id}")
        except Subscription.DoesNotExist:
            logger.warning(f"Subscription {subscription_id} not found")


def handle_payment_failed(invoice):
    """Handle failed payment."""
    subscription_id = invoice.get('subscription')
    
    if subscription_id:
        try:
            subscription = Subscription.objects.get(stripe_subscription_id=subscription_id)
            subscription.status = 'past_due'
            subscription.save()
            
            logger.warning(f"Payment failed for subscription {subscription_id}")
        except Subscription.DoesNotExist:
            logger.warning(f"Subscription {subscription_id} not found")
