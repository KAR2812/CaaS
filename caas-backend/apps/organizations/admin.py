"""Admin for organizations."""
from django.contrib import admin
from .models import Organization, OrganizationMember, Workspace


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner', 'slug', 'created_at']
    search_fields = ['name', 'slug', 'owner__email']
    readonly_fields = ['slug', 'created_at']


@admin.register(OrganizationMember)
class OrganizationMemberAdmin(admin.ModelAdmin):
    list_display = ['organization', 'user', 'role', 'joined_at']
    list_filter = ['role']


@admin.register(Workspace)
class WorkspaceAdmin(admin.ModelAdmin):
    list_display = ['name', 'organization', 'is_active', 'created_at']
    list_filter = ['is_active']
