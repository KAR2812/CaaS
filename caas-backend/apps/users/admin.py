"""
Admin configuration for user models.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserProfile


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['email', 'username', 'first_name', 'last_name', 'is_staff', 'created_at']
    list_filter = ['is_staff', 'is_superuser', 'is_active', 'created_at']
    search_fields = ['email', 'username', 'first_name', 'last_name']
    ordering = ['-created_at']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Profile', {'fields': ('avatar_url', 'bio', 'twitter_handle', 'linkedin_url')}),
        ('Preferences', {'fields': ('timezone', 'email_notifications')}),
        ('Tracking', {'fields': ('last_login_ip', 'created_at', 'updated_at')}),
    )
    readonly_fields = ['created_at', 'updated_at']


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'public_portfolio', 'portfolio_slug', 'total_content_generated']
    list_filter = ['public_portfolio', 'portfolio_theme']
    search_fields = ['user__email', 'portfolio_slug']
    readonly_fields = ['total_content_generated', 'total_posts_scheduled', 'total_tokens_used', 'created_at', 'updated_at']
