"""URL patterns for organizations API."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'', views.OrganizationViewSet, basename='organization')
router.register(r'workspaces', views.WorkspaceViewSet, basename='workspace')

urlpatterns = [
    path('', include(router.urls)),
]
