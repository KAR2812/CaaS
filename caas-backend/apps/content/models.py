"""
Content models for AI-generated social media content.
"""
import uuid
from django.db import models
from django.conf import settings


class Content(models.Model):
    """
    Main content model for AI-generated social media posts.
    """
    PLATFORM_CHOICES = [
        ('twitter', 'Twitter/X'),
        ('linkedin', 'LinkedIn'),
        ('instagram', 'Instagram'),
    ]
    
    TONE_CHOICES = [
        ('professional', 'Professional'),
        ('casual', 'Casual'),
        ('humorous', 'Humorous'),
        ('inspirational', 'Inspirational'),
        ('educational', 'Educational'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('generated', 'Generated'),
        ('scheduled', 'Scheduled'),
        ('published', 'Published'),
        ('failed', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        related_name='contents'
  )
    workspace = models.ForeignKey(
        'organizations.Workspace',
        on_delete=models.CASCADE,
        related_name='contents',
        null=True,
        blank=True
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='contents'
    )
    
    # Content details
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES)
    prompt = models.TextField(help_text="User's original prompt")
    generated_text = models.TextField()
    tone = models.CharField(max_length=20, choices=TONE_CHOICES)
    audience = models.CharField(max_length=100, blank=True)
    
    # AI metadata
    ai_provider = models.CharField(max_length=20, default='openai')
    tokens_used = models.IntegerField(default=0)
    version = models.IntegerField(default=1)
    
    # Status and visibility
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    is_public = models.BooleanField(default=False)
    
    # Tracking
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'contents'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['organization', 'status']),
            models.Index(fields=['created_by']),
        ]
    
    def __str__(self):
        return f"{self.platform} - {self.id}"


class ContentVersion(models.Model):
    """Version history for content."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    content = models.ForeignKey(Content, on_delete=models.CASCADE, related_name='versions')
    version_number = models.IntegerField()
    generated_text = models.TextField()
    tokens_used = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'content_versions'
        unique_together = ['content', 'version_number']
        ordering = ['-version_number']
