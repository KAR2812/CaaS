/**
 * Job processor for scheduled social media posts.
 */
import { Job } from 'bullmq';
import { ScheduleJobData, JobResult } from '../types';
import { TwitterPlatformAdapter } from '../services/platforms/twitter.platform';
import { LinkedInPlatformAdapter } from '../services/platforms/linkedin.platform';
import { InstagramPlatformAdapter } from '../services/platforms/instagram.platform';
import { DjangoApiClient } from '../services/django-client';

// Platform adapters
const platforms = {
    twitter: new TwitterPlatformAdapter(),
    linkedin: new LinkedInPlatformAdapter(),
    instagram: new InstagramPlatformAdapter(),
};

/**
 * Process a scheduled post job.
 * This function is called by BullMQ worker for each job.
 */
export async function processScheduledPost(
    job: Job<ScheduleJobData, JobResult>
): Promise<JobResult> {
    const { content_id, platform, scheduled_at, access_token } = job.data;

    console.log(`\n📤 Processing job ${job.id} for ${platform}`);
    console.log(`   Content: ${content_id}`);
    console.log(`   Scheduled: ${scheduled_at}`);

    try {
        // Check if it's time to publish (handle early execution)
        const scheduledTime = new Date(scheduled_at).getTime();
        const now = Date.now();
        const timeUntilScheduled = scheduledTime - now;

        // Wait if scheduled time is in the future
        if (timeUntilScheduled > 0) {
            console.log(`⏳ Waiting ${Math.round(timeUntilScheduled / 1000)}s before publishing...`);
            await new Promise(resolve => setTimeout(resolve, timeUntilScheduled));
        }

        // Get platform adapter
        const adapter = platforms[platform as keyof typeof platforms];
        if (!adapter) {
            throw new Error(`Unsupported platform: ${platform}`);
        }

        // Validate access token if provided
        if (access_token) {
            const isValid = await adapter.validateToken(access_token);
            if (!isValid) {
                throw new Error('Invalid or expired access token');
            }
        }

        // Fetch content from Django (in production, might pass content_text directly)
        // For now, assuming content_text is in job data or needs to be fetched
        const contentText = job.data.content_text || 'Sample post content'; // TODO: Fetch from Django

        // Publish the post
        await job.updateProgress(50);
        const result = await adapter.publishPost(contentText, access_token || '');

        await job.updateProgress(100);

        // Send callback to Django
        await DjangoApiClient.sendCallback({
            job_id: job.id!,
            content_id,
            status: result.success ? 'published' : 'failed',
            platform_post_id: result.platform_post_id,
            error: result.error,
            published_at: result.published_at,
        });

        return result;
    } catch (error: any) {
        console.error(`❌ Job ${job.id} failed:`, error.message);

        // Send failure callback to Django
        await DjangoApiClient.sendCallback({
            job_id: job.id!,
            content_id,
            status: 'failed',
            error: error.message,
        });

        // Return failure result
        return {
            success: false,
            error: error.message,
        };
    }
}
