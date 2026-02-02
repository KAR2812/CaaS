"""Admin for scheduling."""
from django.contrib import admin
from .models import ScheduledPost


@admin.register(ScheduledPost)
class ScheduledPostAdmin(admin.ModelAdmin):
    list_display = ['content', 'platform', 'scheduled_at', 'status', 'published_at']
    list_filter = ['status', 'platform']
    search_fields = ['content__id', 'job_id', 'platform_post_id']
    readonly_fields = ['id', 'job_id', 'published_at', 'created_at']
