"""Scheduling models - metadata only, actual jobs in Node.js."""
import uuid
from django.db import models
from django.conf import settings


class ScheduledPost(models.Model):
    """Metadata for scheduled social media posts."""
    STATUS_CHOICES = [
        ('queued', 'Queued'),
        ('scheduled', 'Scheduled'),
        ('published', 'Published'),
        ('failed', 'Failed'),
        ('canceled', 'Canceled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    content = models.ForeignKey(
        'content.Content',
        on_delete=models.CASCADE,
        related_name='scheduled_posts'
    )
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        related_name='scheduled_posts'
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='scheduled_posts'
    )
    
    # Scheduling
    platform = models.CharField(max_length=20)
    scheduled_at = models.DateTimeField()
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='queued')
    job_id = models.CharField(max_length=255, blank=True, help_text="BullMQ job ID from Node.js")
    
    # Publishing result
    platform_post_id = models.CharField(max_length=255, blank=True)
    published_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'scheduled_posts'
        ordering = ['scheduled_at']
        indexes = [
            models.Index(fields=['organization', 'status']),
            models.Index(fields=['scheduled_at']),
        ]
    
    def __str__(self):
        return f"{self.content.platform} - {self.scheduled_at}"
