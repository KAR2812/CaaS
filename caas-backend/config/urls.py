"""
URL configuration for CaaS project.
"""
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    
    # API v1
    path('api/v1/auth/', include('apps.users.urls')),
    path('api/v1/organizations/', include('apps.organizations.urls')),
    path('api/v1/content/', include('apps.content.urls')),
    path('api/v1/subscriptions/', include('apps.subscriptions.urls')),
    path('api/v1/scheduling/', include('apps.scheduling.urls')),
]
