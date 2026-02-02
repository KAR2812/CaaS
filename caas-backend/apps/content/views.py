"""
Views for AI content generation and management.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction

from .models import Content, ContentVersion
from .serializers import (
    ContentSerializer, ContentGenerateSerializer,
    ContentRegenerateSerializer
)
from .ai_service import AIContentGenerator
from apps.organizations.models import Organization, Workspace
from apps.organizations.permissions import IsOrganizationMember


class ContentViewSet(viewsets.ModelViewSet):
    """ViewSet for content CRUD operations and AI generation."""
    serializer_class = ContentSerializer
    permission_classes = [IsAuthenticated, IsOrganizationMember]
    
    def get_queryset(self):
        """Filter content by user's organizations."""
        user = self.request.user
        org_ids = user.organization_memberships.values_list('organization_id', flat=True)
        return Content.objects.filter(organization_id__in=org_ids)
    
    @action(detail=False, methods=['post'])
    def generate(self, request):
        """
        Generate new AI content.
        POST /api/v1/content/generate/
        """
        serializer = ContentGenerateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        
        # Verify organization access
        try:
            org = Organization.objects.get(id=data['organization_id'])
            if not org.members.filter(user=request.user).exists():
                return Response(
                    {'error': 'Access denied to this organization'},
                    status=status.HTTP_403_FORBIDDEN
                )
        except Organization.DoesNotExist:
            return Response(
                {'error': 'Organization not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check token quota (simplified - should check subscription)
        # TODO: Add subscription quota check
        
        # Generate content with AI
        result = AIContentGenerator.generate(
            platform=data['platform'],
            tone=data['tone'],
            audience=data.get('audience', ''),
            user_prompt=data['prompt'],
            provider=data.get('ai_provider', 'openai')
        )
        
        if not result['success']:
            return Response(
                {'error': f"AI generation failed: {result.get('error', 'Unknown error')}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # Create content record
        with transaction.atomic():
            content = Content.objects.create(
                organization=org,
                workspace_id=data.get('workspace_id'),
                created_by=request.user,
                platform=data['platform'],
                prompt=data['prompt'],
                generated_text=result['text'],
                tone=data['tone'],
                audience=data.get('audience', ''),
                ai_provider=result['provider'],
                tokens_used=result['tokens'],
                status='generated'
            )
            
            # Create first version
            ContentVersion.objects.create(
                content=content,
                version_number=1,
                generated_text=result['text'],
                tokens_used=result['tokens']
            )
        
        return Response(
            ContentSerializer(content).data,
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=True, methods=['post'])
    def regenerate(self, request, pk=None):
        """
        Regenerate content with modifications.
        POST /api/v1/content/{id}/regenerate/
        """
        content = self.get_object()
        serializer = ContentRegenerateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        modification = serializer.validated_data['modification_prompt']
        new_prompt = f"{content.prompt}\n\nModification: {modification}"
        
        # Generate new version
        result = AIContentGenerator.generate(
            platform=content.platform,
            tone=content.tone,
            audience=content.audience,
            user_prompt=new_prompt,
            provider=content.ai_provider
        )
        
        if not result['success']:
            return Response(
                {'error': f"Regeneration failed: {result.get('error')}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # Update content and create new version
        with transaction.atomic():
            content.generated_text = result['text']
            content.version += 1
            content.tokens_used += result['tokens']
            content.save()
            
            ContentVersion.objects.create(
                content=content,
                version_number=content.version,
                generated_text=result['text'],
                tokens_used=result['tokens']
            )
        
        return Response(ContentSerializer(content).data)
