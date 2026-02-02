"""
Serializers for organizations and workspaces.
"""
from rest_framework import serializers
from .models import Organization, OrganizationMember, Workspace


class OrganizationMemberSerializer(serializers.ModelSerializer):
    """Serializer for organization members."""
    email = serializers.EmailField(source='user.email', read_only=True)
    full_name = serializers.CharField(source='user.full_name', read_only=True)
    
    class Meta:
        model = OrganizationMember
        fields = ['id', 'user', 'email', 'full_name', 'role', 'joined_at']
        read_only_fields = ['id', 'joined_at']


class WorkspaceSerializer(serializers.ModelSerializer):
    """Serializer for workspaces."""
    
    class Meta:
        model = Workspace
        fields = ['id', 'organization', 'name', 'slug', 'description', 'is_active', 'created_at']
        read_only_fields = ['id', 'slug', 'created_at']


class OrganizationSerializer(serializers.ModelSerializer):
    """Serializer for organizations."""
    members_count = serializers.SerializerMethodField()
    workspaces = WorkspaceSerializer(many=True, read_only=True)
    
    class Meta:
        model = Organization
        fields = [
            'id', 'name', 'slug', 'owner', 'description', 'logo_url',
            'website', 'members_count', 'workspaces', 'created_at'
        ]
        read_only_fields = ['id', 'slug', 'owner', 'created_at']
    
    def get_members_count(self, obj):
        return obj.members.count()
