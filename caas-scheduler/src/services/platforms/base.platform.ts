/**
 * Base platform adapter interface.
 */
import { JobResult } from '../../types';

export abstract class BasePlatformAdapter {
    abstract platform: string;

    /**
     * Publish a post to the platform.
     */
    abstract publishPost(text: string, accessToken: string): Promise<JobResult>;

    /**
     * Validate that an access token is valid.
     */
    abstract validateToken(accessToken: string): Promise<boolean>;

    /**
     * Generic error handler for platform API calls.
     */
    protected handleError(error: any, platform: string): JobResult {
        console.error(`${platform} API error:`, error);

        const errorMessage = error.response?.data?.message || error.message || 'Unknown error';

        return {
            success: false,
            error: `${platform} publishing failed: ${errorMessage}`,
        };
    }
}
