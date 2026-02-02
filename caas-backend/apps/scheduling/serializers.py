"""Serializers for scheduling."""
from rest_framework import serializers
from .models import ScheduledPost


class ScheduledPostSerializer(serializers.ModelSerializer):
    """Serializer for scheduled posts."""
    
    class Meta:
        model = ScheduledPost
        fields = ['id', 'content', 'organization', 'created_by', 'platform',
                  'scheduled_at', 'status', 'job_id', 'platform_post_id',
                  'published_at', 'error_message', 'created_at']
        read_only_fields = ['id', 'created_by', 'status', 'job_id', 
                           'platform_post_id', 'published_at', 'created_at']


class SchedulePostRequestSerializer(serializers.Serializer):
    """Serializer for scheduling request."""
    content_id = serializers.UUIDField()
    scheduled_at = serializers.DateTimeField()
    platform_access_token = serializers.CharField(required=False, allow_blank=True)
