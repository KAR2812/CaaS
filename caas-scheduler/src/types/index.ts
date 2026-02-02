/**
 * TypeScript type definitions for the scheduler service.
 */

export interface ScheduleJobData {
    content_id: string;
    platform: 'twitter' | 'linkedin' | 'instagram';
    scheduled_at: string;  // ISO 8601
    user_id: string;
    org_id: string;
    access_token?: string;  // Platform-specific OAuth token
    content_text?: string;
}

export interface JobResult {
    success: boolean;
    platform_post_id?: string;
    error?: string;
    published_at?: string;
}

export interface PlatformAdapter {
    platform: string;
    publishPost(text: string, accessToken: string): Promise<JobResult>;
    validateToken(accessToken: string): Promise<boolean>;
}

export interface DjangoCallbackPayload {
    job_id: string;
    content_id: string;
    status: 'published' | 'failed';
    platform_post_id?: string;
    error?: string;
    published_at?: string;
}

export interface AuthenticatedRequest extends Express.Request {
    user?: {
        id: string;
        email: string;
    };
}
