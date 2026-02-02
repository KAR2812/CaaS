"""
Stripe service for payment processing.
"""
import stripe
import logging
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY
logger = logging.getLogger(__name__)


class StripeService:
    """Service for Stripe payment operations."""
    
    @staticmethod
    def create_customer(email, name):
        """Create a Stripe customer."""
        try:
            customer = stripe.Customer.create(
                email=email,
                name=name
            )
            return {'success': True, 'customer_id': customer.id}
        except stripe.error.StripeError as e:
            logger.error(f"Stripe customer creation failed: {e}")
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def create_checkout_session(customer_id, price_id, organization_id, success_url, cancel_url):
        """Create a Stripe Checkout session for subscription."""
        try:
            session = stripe.checkout.Session.create(
                customer=customer_id,
                payment_method_types=['card'],
                line_items=[{
                    'price': price_id,
                    'quantity': 1,
                }],
                mode='subscription',
                success_url=success_url,
                cancel_url=cancel_url,
                metadata={
                    'organization_id': str(organization_id)
                }
            )
            return {'success': True, 'session_id': session.id, 'url': session.url}
        except stripe.error.StripeError as e:
            logger.error(f"Checkout session creation failed: {e}")
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def cancel_subscription(subscription_id, at_period_end=True):
        """Cancel a Stripe subscription."""
        try:
            subscription = stripe.Subscription.modify(
                subscription_id,
                cancel_at_period_end=at_period_end
            )
            return {'success': True, 'subscription': subscription}
        except stripe.error.StripeError as e:
            logger.error(f"Subscription cancellation failed: {e}")
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def verify_webhook_signature(payload, sig_header):
        """Verify Stripe webhook signature."""
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
            return {'success': True, 'event': event}
        except ValueError as e:
            return {'success': False, 'error': 'Invalid payload'}
        except stripe.error.SignatureVerificationError as e:
            return {'success': False, 'error': 'Invalid signature'}
