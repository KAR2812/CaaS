"""URLs for scheduling."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'', views.ScheduledPostViewSet, basename='scheduled-post')

urlpatterns = [
    path('callback/', views.callback, name='scheduling-callback'),
    path('', include(router.urls)),
]
