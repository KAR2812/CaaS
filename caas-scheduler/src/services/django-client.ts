/**
 * HTTP client for Django API callbacks.
 */
import axios from 'axios';
import { DjangoCallbackPayload } from '../types';

const DJANGO_API_URL = process.env.DJANGO_API_URL || 'http://localhost:8000';
const SERVICE_TOKEN = process.env.SERVICE_TOKEN || '';

export class DjangoApiClient {
    /**
     * Send callback to Django when job completes.
     */
    static async sendCallback(payload: DjangoCallbackPayload): Promise<void> {
        try {
            await axios.post(
                `${DJANGO_API_URL}/api/v1/scheduling/callback/`,
                payload,
                {
                    headers: {
                        'Content-Type': 'application/json',
                        'X-Service-Token': SERVICE_TOKEN,
                    },
                    timeout: 10000,
                }
            );

            console.log(`✅ Django callback sent for job ${payload.job_id}`);
        } catch (error: any) {
            console.error('❌ Django callback failed:', error.message);
            // Don't throw - this is a non-critical operation
            // The job has already completed, callback failure shouldn't fail the job
        }
    }

    /**
     * Fetch content details from Django (if needed).
     */
    static async getContent(contentId: string, userToken: string): Promise<any> {
        try {
            const response = await axios.get(
                `${DJANGO_API_URL}/api/v1/content/${contentId}/`,
                {
                    headers: {
                        'Authorization': `Bearer ${userToken}`,
                    },
                    timeout: 5000,
                }
            );

            return response.data;
        } catch (error: any) {
            console.error('Failed to fetch content from Django:', error.message);
            throw error;
        }
    }
}
