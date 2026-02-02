"""URLs for subscriptions."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views, webhooks

router = DefaultRouter()
router.register(r'plans', views.PlanViewSet)
router.register(r'', views.SubscriptionViewSet, basename='subscription')

urlpatterns = [
    path('webhook/', webhooks.stripe_webhook, name='stripe-webhook'),
    path('', include(router.urls)),
]
