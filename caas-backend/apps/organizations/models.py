"""
Organization and workspace models for multi-tenancy.
"""
import uuid
from django.db import models
from django.conf import settings
from django.utils.text import slugify


class Organization(models.Model):
    """
    Organization model for multi-tenancy.
    Each organization can have multiple workspaces and members.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, max_length=100)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='owned_organizations'
    )
    
    # Settings
    description = models.TextField(blank=True)
    logo_url = models.URLField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    
    # Tracking
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'organizations'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['owner']),
        ]
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class OrganizationMember(models.Model):
    """
    Membership model linking users to organizations with roles.
    """
    ROLE_CHOICES = [
        ('owner', 'Owner'),
        ('admin', 'Admin'),
        ('member', 'Member'),
        ('viewer', 'Viewer'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='members'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='organization_memberships'
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member')
    
    # Tracking
    joined_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'organization_members'
        unique_together = ['organization', 'user']
        ordering = ['-joined_at']
        indexes = [
            models.Index(fields=['organization', 'user']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.organization.name} ({self.role})"


class Workspace(models.Model):
    """
    Workspace model for organizing content within an organization.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='workspaces'
    )
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=100)
    description = models.TextField(blank=True)
    
    # Settings
    is_active = models.BooleanField(default=True)
    
    # Tracking
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_workspaces'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'workspaces'
        unique_together = ['organization', 'slug']
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['organization', 'slug']),
        ]
    
    def __str__(self):
        return f"{self.organization.name} / {self.name}"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
