"""
User models for authentication and profile management.
"""
import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom user model extending Django's AbstractUser.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, db_index=True)
    
    # Profile fields
    avatar_url = models.URLField(blank=True, null=True)
    bio = models.TextField(blank=True)
    
    # Social links
    twitter_handle = models.CharField(max_length=100, blank=True)
    linkedin_url = models.URLField(blank=True)
    
    # Preferences
    timezone = models.CharField(max_length=50, default='UTC')
    email_notifications = models.BooleanField(default=True)
    
    # Tracking
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login_ip = models.GenericIPAddressField(blank=True, null=True)
    
    # Override username requirement - use email as primary identifier
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    
    class Meta:
        db_table = 'users'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.email} ({self.get_full_name()})"
    
    @property
    def full_name(self):
        return self.get_full_name() or self.email


class UserProfile(models.Model):
    """
    Extended profile information for users.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Public portfolio settings
    public_portfolio = models.BooleanField(default=False)
    portfolio_slug = models.SlugField(unique=True, blank=True, null=True)
    portfolio_bio = models.TextField(blank=True)
    portfolio_theme = models.CharField(max_length=20, default='light', choices=[
        ('light', 'Light'),
        ('dark', 'Dark'),
    ])
    
    # Analytics
    total_content_generated = models.IntegerField(default=0)
    total_posts_scheduled = models.IntegerField(default=0)
    total_tokens_used = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_profiles'
    
    def __str__(self):
        return f"Profile for {self.user.email}"
