"""
Serializers for content generation and management.
"""
from rest_framework import serializers
from .models import Content, ContentVersion


class ContentVersionSerializer(serializers.ModelSerializer):
    """Serializer for content versions."""
    
    class Meta:
        model = ContentVersion
        fields = ['id', 'version_number', 'generated_text', 'tokens_used', 'created_at']
        read_only_fields = ['id', 'created_at']


class ContentSerializer(serializers.ModelSerializer):
    """Serializer for content."""
    versions = ContentVersionSerializer(many=True, read_only=True)
    
    class Meta:
        model = Content
        fields = [
            'id', 'organization', 'workspace', 'created_by', 'platform',
            'prompt', 'generated_text', 'tone', 'audience', 'ai_provider',
            'tokens_used', 'version', 'status', 'is_public', 'versions',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at', 'tokens_used']


class ContentGenerateSerializer(serializers.Serializer):
    """Serializer for AI content generation requests."""
    platform = serializers.ChoiceField(choices=Content.PLATFORM_CHOICES)
    tone = serializers.ChoiceField(choices=Content.TONE_CHOICES)
    prompt = serializers.CharField()
    audience = serializers.CharField(required=False, allow_blank=True)
    organization_id = serializers.UUIDField()
    workspace_id = serializers.UUIDField(required=False, allow_null=True)
    ai_provider = serializers.ChoiceField(choices=['openai', 'gemini'], default='openai')


class ContentRegenerateSerializer(serializers.Serializer):
    """Serializer for content regeneration."""
    modification_prompt = serializers.CharField(
        help_text="What to change (e.g., 'make it more casual', 'add emojis')"
    )
