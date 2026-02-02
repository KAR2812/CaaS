/**
 * Instagram platform adapter (MOCK).
 * Instagram Graph API has strict limitations and requires Facebook Business account.
 * This is a mock implementation for the MVP.
 */
import { BasePlatformAdapter } from './base.platform';
import { JobResult } from '../../types';

export class InstagramPlatformAdapter extends BasePlatformAdapter {
    platform = 'instagram';

    async publishPost(text: string, accessToken: string): Promise<JobResult> {
        // MOCK IMPLEMENTATION
        // In production, this would use Instagram Graph API:
        // https://developers.facebook.com/docs/instagram-api/guides/content-publishing

        console.log('📸 [MOCK] Instagram post:', text.substring(0, 50) + '...');

        // Simulate API delay
        await new Promise(resolve => setTimeout(resolve, 500));

        // Simulate 90% success rate
        if (Math.random() > 0.1) {
            return {
                success: true,
                platform_post_id: `mock_ig_${Date.now()}`,
                published_at: new Date().toISOString(),
            };
        } else {
            return {
                success: false,
                error: 'Instagram mock: Simulated API failure',
            };
        }
    }

    async validateToken(accessToken: string): Promise<boolean> {
        // Mock always validates for now
        return accessToken.length > 0;
    }
}
