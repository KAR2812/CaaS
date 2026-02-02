"""Subscription views."""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.conf import settings

from .models import Plan, Subscription
from .serializers import PlanSerializer, SubscriptionSerializer
from .stripe_service import StripeService
from apps.organizations.models import Organization


class PlanViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for listing available plans."""
    queryset = Plan.objects.filter(is_active=True)
    serializer_class = PlanSerializer
    permission_classes = [IsAuthenticated]


class SubscriptionViewSet(viewsets.ModelViewSet):
    """ViewSet for subscription management."""
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        org_ids = self.request.user.organization_memberships.values_list('organization_id', flat=True)
        return Subscription.objects.filter(organization_id__in=org_ids)
    
    @action(detail=False, methods=['post'])
    def create_checkout_session(self, request):
        """Create Stripe checkout session for upgrading."""
        org_id = request.data.get('organization_id')
        plan_id = request.data.get('plan_id')
        
        try:
            org = Organization.objects.get(id=org_id)
            plan = Plan.objects.get(id=plan_id)
            
            # Create Stripe customer if needed
            subscription = Subscription.objects.filter(organization=org).first()
            if not subscription or not subscription.stripe_customer_id:
                customer_result = StripeService.create_customer(
                    email=org.owner.email,
                    name=org.name
                )
                if not customer_result['success']:
                    return Response({'error': customer_result['error']}, 
                                    status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                customer_id = customer_result['customer_id']
            else:
                customer_id = subscription.stripe_customer_id
            
            # Create checkout session
            success_url = f"{settings.FRONTEND_EDITOR_URL}/subscription/success"
            cancel_url = f"{settings.FRONTEND_EDITOR_URL}/subscription/cancel"
            
            session_result = StripeService.create_checkout_session(
                customer_id=customer_id,
                price_id=plan.stripe_price_id,
                organization_id=org_id,
                success_url=success_url,
                cancel_url=cancel_url
            )
            
            if session_result['success']:
                return Response({'checkout_url': session_result['url']})
            else:
                return Response({'error': session_result['error']}, 
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        except (Organization.DoesNotExist, Plan.DoesNotExist) as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
