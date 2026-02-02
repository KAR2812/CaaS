"""
Client for communicating with Node.js scheduler service.
"""
import requests
import logging
from django.conf import settings
from rest_framework_simplejwt.tokens import AccessToken

logger = logging.getLogger(__name__)


class SchedulerClient:
    """HTTP client for Node.js scheduler service."""
    
    BASE_URL = settings.SCHEDULER_SERVICE_URL
    SERVICE_TOKEN = settings.SCHEDULER_SERVICE_TOKEN
    
    @staticmethod
    def _get_headers(user):
        """Generate headers with service authentication."""
        # Create JWT for service-to-service communication
        token = AccessToken.for_user(user)
        return {
            'Authorization': f'Bearer {str(token)}',
            'Content-Type': 'application/json',
            'X-Service-Token': SchedulerClient.SERVICE_TOKEN
        }
    
    @staticmethod
    def schedule_post(content_id, platform, scheduled_at, user, org_id, access_token=None):
        """
        Schedule a post via Node.js scheduler.
        
        Args:
            content_id: UUID of content
            platform: twitter, linkedin, instagram
            scheduled_at: ISO 8601 datetime string
            user: User object
            org_id: Organization UUID
            access_token: Platform-specific OAuth token
        
        Returns:
            dict with success, job_id
        """
        url = f"{SchedulerClient.BASE_URL}/api/v1/schedule"
        headers = SchedulerClient._get_headers(user)
        
        payload = {
            'content_id': str(content_id),
            'platform': platform,
            'scheduled_at': scheduled_at,
            'user_id': str(user.id),
            'org_id': str(org_id),
            'access_token': access_token or ''  # Platform OAuth token
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            return {
                'success': True,
                'job_id': data.get('job_id'),
                'status': data.get('status', 'scheduled')
            }
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Scheduler service error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def cancel_job(job_id, user):
        """Cancel a scheduled job."""
        url = f"{SchedulerClient.BASE_URL}/api/v1/schedule/{job_id}"
        headers = SchedulerClient._get_headers(user)
        
        try:
            response = requests.delete(url, headers=headers, timeout=10)
            response.raise_for_status()
            return {'success': True}
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Job cancellation error: {e}")
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def get_job_status(job_id, user):
        """Get status of a scheduled job."""
        url = f"{SchedulerClient.BASE_URL}/api/v1/schedule/{job_id}"
        headers = SchedulerClient._get_headers(user)
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            return {'success': True, 'data': response.json()}
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Job status fetch error: {e}")
            return {'success': False, 'error': str(e)}
