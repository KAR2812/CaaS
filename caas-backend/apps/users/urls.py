"""
URL patterns for user authentication.
"""
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views

urlpatterns = [
    # Authentication
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', TokenObtainPairView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    
    # Profile
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('profile/details/', views.UserProfileDetailView.as_view(), name='profile-details'),
    
    # Password
    path('password/change/', views.PasswordChangeView.as_view(), name='password-change'),
]
