/**
 * LinkedIn platform adapter.
 * Note: LinkedIn API requires organization access approval.
 * This is a simplified implementation.
 */
import axios from 'axios';
import { BasePlatformAdapter } from './base.platform';
import { JobResult } from '../../types';

export class LinkedInPlatformAdapter extends BasePlatformAdapter {
    platform = 'linkedin';

    async publishPost(text: string, accessToken: string): Promise<JobResult> {
        try {
            // Get user profile URN
            const profileResponse = await axios.get('https://api.linkedin.com/v2/me', {
                headers: {
                    'Authorization': `Bearer ${accessToken}`,
                    'X-Restli-Protocol-Version': '2.0.0'
                }
            });

            const authorUrn = `urn:li:person:${profileResponse.data.id}`;

            // Create share/post
            const shareResponse = await axios.post(
                'https://api.linkedin.com/v2/ugcPosts',
                {
                    author: authorUrn,
                    lifecycleState: 'PUBLISHED',
                    specificContent: {
                        'com.linkedin.ugc.ShareContent': {
                            shareCommentary: {
                                text: text
                            },
                            shareMediaCategory: 'NONE'
                        }
                    },
                    visibility: {
                        'com.linkedin.ugc.MemberNetworkVisibility': 'PUBLIC'
                    }
                },
                {
                    headers: {
                        'Authorization': `Bearer ${accessToken}`,
                        'Content-Type': 'application/json',
                        'X-Restli-Protocol-Version': '2.0.0'
                    }
                }
            );

            return {
                success: true,
                platform_post_id: shareResponse.data.id,
                published_at: new Date().toISOString(),
            };
        } catch (error) {
            return this.handleError(error, 'LinkedIn');
        }
    }

    async validateToken(accessToken: string): Promise<boolean> {
        try {
            await axios.get('https://api.linkedin.com/v2/me', {
                headers: { 'Authorization': `Bearer ${accessToken}` }
            });
            return true;
        } catch {
            return false;
        }
    }
}
