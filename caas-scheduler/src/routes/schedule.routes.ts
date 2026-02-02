/**
 * Routes for scheduling API.
 */
import { Router, Request, Response } from 'express';
import schedulerQueue, { getQueueHealth } from '../queues/scheduler.queue';
import { ScheduleJobData } from '../types';
import { authenticateJWT } from '../middleware/auth.middleware';

const router = Router();

/**
 * POST /api/v1/schedule
 * Schedule a new post.
 */
router.post('/schedule', authenticateJWT, async (req: Request, res: Response) => {
    try {
        const jobData: ScheduleJobData = req.body;

        // Validate required fields
        if (!jobData.content_id || !jobData.platform || !jobData.scheduled_at) {
            res.status(400).json({ error: 'Missing required fields' });
            return;
        }

        // Calculate delay until scheduled time
        const scheduledTime = new Date(jobData.scheduled_at).getTime();
        const now = Date.now();
        const delay = Math.max(0, scheduledTime - now);

        // Add job to queue
        const job = await schedulerQueue.add('schedule-post', jobData, {
            delay,
            jobId: `${jobData.content_id}-${scheduledTime}`, // Prevent duplicates
        });

        res.status(201).json({
            job_id: job.id,
            status: 'scheduled',
            scheduled_at: jobData.scheduled_at,
        });
    } catch (error: any) {
        console.error('Schedule error:', error);
        res.status(500).json({ error: error.message });
    }
});

/**
 * GET /api/v1/schedule/:jobId
 * Get job status.
 */
router.get('/schedule/:jobId', authenticateJWT, async (req: Request, res: Response) => {
    try {
        const { jobId } = req.params;
        const job = await schedulerQueue.getJob(jobId);

        if (!job) {
            res.status(404).json({ error: 'Job not found' });
            return;
        }

        const state = await job.getState();
        const progress = job.progress;

        res.json({
            job_id: job.id,
            status: state,
            progress,
            data: job.data,
            created_at: job.timestamp,
            processed_on: job.processedOn,
            finished_on: job.finishedOn,
            return_value: job.returnvalue,
        });
    } catch (error: any) {
        res.status(500).json({ error: error.message });
    }
});

/**
 * DELETE /api/v1/schedule/:jobId
 * Cancel a scheduled job.
 */
router.delete('/schedule/:jobId', authenticateJWT, async (req: Request, res: Response) => {
    try {
        const { jobId } = req.params;
        const job = await schedulerQueue.getJob(jobId);

        if (!job) {
            res.status(404).json({ error: 'Job not found' });
            return;
        }

        const state = await job.getState();

        // Can only cancel waiting or delayed jobs
        if (state !== 'waiting' && state !== 'delayed') {
            res.status(400).json({
                error: `Cannot cancel job in state: ${state}`,
                current_state: state
            });
            return;
        }

        await job.remove();

        res.json({
            message: 'Job canceled successfully',
            job_id: jobId
        });
    } catch (error: any) {
        res.status(500).json({ error: error.message });
    }
});

/**
 * GET /api/v1/health
 * Queue health check.
 */
router.get('/health', async (req: Request, res: Response) => {
    try {
        const health = await getQueueHealth();

        res.json({
            status: 'healthy',
            service: 'scheduler',
            queue: health,
            timestamp: new Date().toISOString(),
        });
    } catch (error: any) {
        res.status(500).json({
            status: 'unhealthy',
            error: error.message,
        });
    }
});

export default router;
