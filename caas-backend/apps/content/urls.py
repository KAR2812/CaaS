"""
URL patterns for content API.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'', views.ContentViewSet, basename='content')

urlpatterns = [
    path('', include(router.urls)),
]
