/**
 * Twitter/X platform adapter using Twitter API v2.
 */
import { TwitterApi } from 'twitter-api-v2';
import { BasePlatformAdapter } from './base.platform';
import { JobResult } from '../../types';

export class TwitterPlatformAdapter extends BasePlatformAdapter {
    platform = 'twitter';

    async publishPost(text: string, accessToken: string): Promise<JobResult> {
        try {
            // In production, use user's OAuth token
            // For now, using mock/bearer token approach
            const client = new TwitterApi(accessToken || process.env.TWITTER_BEARER_TOKEN!);

            // Tweet the content
            const tweet = await client.v2.tweet(text);

            return {
                success: true,
                platform_post_id: tweet.data.id,
                published_at: new Date().toISOString(),
            };
        } catch (error) {
            return this.handleError(error, 'Twitter');
        }
    }

    async validateToken(accessToken: string): Promise<boolean> {
        try {
            const client = new TwitterApi(accessToken);
            await client.v2.me();
            return true;
        } catch {
            return false;
        }
    }
}
