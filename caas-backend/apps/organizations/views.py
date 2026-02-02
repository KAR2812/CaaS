"""
Views for organization and workspace management.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction

from .models import Organization, OrganizationMember, Workspace
from .serializers import OrganizationSerializer, WorkspaceSerializer, OrganizationMemberSerializer
from .permissions import IsOrganizationOwnerOrAdmin


class OrganizationViewSet(viewsets.ModelViewSet):
    """ViewSet for organization management."""
    serializer_class = OrganizationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Return organizations where user is a member."""
        return Organization.objects.filter(members__user=self.request.user)
    
    def perform_create(self, serializer):
        """Create organization and add creator as owner."""
        with transaction.atomic():
            org = serializer.save(owner=self.request.user)
            OrganizationMember.objects.create(
                organization=org,
                user=self.request.user,
                role='owner'
            )
    
    @action(detail=True, methods=['get'])
    def members(self, request, pk=None):
        """Get organization members."""
        org = self.get_object()
        members = org.members.all()
        serializer = OrganizationMemberSerializer(members, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def invite(self, request, pk=None):
        """Invite user to organization (simplified - just add by email)."""
        org = self.get_object()
        # Check permission
        if not org.members.filter(user=request.user, role__in=['owner', 'admin']).exists():
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        # TODO: Implement proper invitation system with email
        return Response({'message': 'Invitation feature coming soon'})


class WorkspaceViewSet(viewsets.ModelViewSet):
    """ViewSet for workspace management."""
    serializer_class = WorkspaceSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Return workspaces from user's organizations."""
        org_ids = self.request.user.organization_memberships.values_list('organization_id', flat=True)
        return Workspace.objects.filter(organization_id__in=org_ids)
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
