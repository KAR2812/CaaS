"""
Custom permissions for organization access control.
"""
from rest_framework import permissions


class IsOrganizationOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow owners or admins of an organization to edit it.
    """
    
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any authenticated user in the organization
        if request.method in permissions.SAFE_METHODS:
            return obj.members.filter(user=request.user).exists()
        
        # Write permissions are only allowed to owners and admins
        membership = obj.members.filter(user=request.user).first()
        return membership and membership.role in ['owner', 'admin']


class IsOrganizationMember(permissions.BasePermission):
    """
    Permission to check if user is a member of the organization.
    """
    
    def has_object_permission(self, request, view, obj):
        # Check if obj is an Organization or has organization attribute
        organization = obj if hasattr(obj, 'members') else getattr(obj, 'organization', None)
        if organization:
            return organization.members.filter(user=request.user).exists()
        return False
