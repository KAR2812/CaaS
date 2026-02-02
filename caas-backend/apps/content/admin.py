"""Admin configuration for content models."""
from django.contrib import admin
from .models import Content, ContentVersion


@admin.register(Content)
class ContentAdmin(admin.ModelAdmin):
    list_display = ['platform', 'organization', 'created_by', 'status', 'tokens_used', 'created_at']
    list_filter = ['platform', 'status', 'tone', 'ai_provider']
    search_fields = ['generated_text', 'prompt', 'created_by__email']
    readonly_fields = ['id', 'created_at', 'updated_at']
    

@admin.register(ContentVersion)
class ContentVersionAdmin(admin.ModelAdmin):
    list_display = ['content', 'version_number', 'tokens_used', 'created_at']
    list_filter = ['created_at']
    readonly_fields = ['id', 'created_at']
