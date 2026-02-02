"""Views for scheduling."""
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone

from .models import ScheduledPost
from .serializers import ScheduledPostSerializer, SchedulePostRequestSerializer
from .scheduler_client import SchedulerClient
from apps.content.models import Content


class ScheduledPostViewSet(viewsets.ModelViewSet):
    """ViewSet for scheduled posts."""
    serializer_class = ScheduledPostSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        org_ids = self.request.user.organization_memberships.values_list('organization_id', flat=True)
        return ScheduledPost.objects.filter(organization_id__in=org_ids)
    
    @action(detail=False, methods=['post'])
    def schedule(self, request):
        """Schedule a post via Node.js service."""
        serializer = SchedulePostRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        content_id = serializer.validated_data['content_id']
        scheduled_at = serializer.validated_data['scheduled_at']
        platform_token = serializer.validated_data.get('platform_access_token', '')
        
        # Get content
        try:
            content = Content.objects.get(id=content_id)
        except Content.DoesNotExist:
            return Response({'error': 'Content not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Create scheduled post record
        scheduled_post = ScheduledPost.objects.create(
            content=content,
            organization=content.organization,
            created_by=request.user,
            platform=content.platform,
            scheduled_at=scheduled_at,
            status='queued'
        )
        
        # Send to Node.js scheduler
        result = SchedulerClient.schedule_post(
            content_id=content_id,
            platform=content.platform,
            scheduled_at=scheduled_at.isoformat(),
            user=request.user,
            org_id=content.organization.id,
            access_token=platform_token
        )
        
        if result['success']:
            scheduled_post.job_id = result['job_id']
            scheduled_post.status = 'scheduled'
            scheduled_post.save()
            
            return Response(ScheduledPostSerializer(scheduled_post).data, 
                          status=status.HTTP_201_CREATED)
        else:
            scheduled_post.status = 'failed'
            scheduled_post.error_message = result.get('error', 'Unknown error')
            scheduled_post.save()
            
            return Response(
                {'error': f"Scheduling failed: {result.get('error')}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel a scheduled post."""
        scheduled_post = self.get_object()
        
        if scheduled_post.status in ['published', 'canceled']:
            return Response(
                {'error': 'Cannot cancel already published or canceled post'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        result = SchedulerClient.cancel_job(scheduled_post.job_id, request.user)
        
        if result['success']:
            scheduled_post.status = 'canceled'
            scheduled_post.save()
            return Response({'message': 'Post canceled successfully'})
        else:
            return Response({'error': result.get('error')}, 
                          status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def callback(request):
    """
    Callback endpoint for Node.js scheduler to update job status.
    POST /api/v1/scheduling/callback/
    """
    job_id = request.data.get('job_id')
    content_id = request.data.get('content_id')
    job_status = request.data.get('status')
    platform_post_id = request.data.get('platform_post_id')
    error = request.data.get('error')
    
    try:
        scheduled_post = ScheduledPost.objects.get(job_id=job_id)
        scheduled_post.status = job_status
        
        if job_status == 'published':
            scheduled_post.platform_post_id = platform_post_id
            scheduled_post.published_at = timezone.now()
        elif job_status == 'failed':
            scheduled_post.error_message = error
        
        scheduled_post.save()
        
        return Response({'message': 'Callback processed'}, status=status.HTTP_200_OK)
    
    except ScheduledPost.DoesNotExist:
        return Response({'error': 'Scheduled post not found'}, status=status.HTTP_404_NOT_FOUND)
