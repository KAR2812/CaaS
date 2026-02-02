/**
 * BullMQ queue for social media post scheduling.
 */
import { Queue, Worker, Job, QueueEvents } from 'bullmq';
import redisConnection from '../config/redis';
import { ScheduleJobData, JobResult } from '../types';
import { processScheduledPost } from './processor';

const QUEUE_NAME = 'social-posts';

// Create queue
export const schedulerQueue = new Queue<ScheduleJobData>(QUEUE_NAME, {
    connection: redisConnection,
    defaultJobOptions: {
        attempts: parseInt(process.env.JOB_RETRY_ATTEMPTS || '3'),
        backoff: {
            type: 'exponential',
            delay: parseInt(process.env.JOB_RETRY_DELAY || '60000'), // 1 minute
        },
        removeOnComplete: {
            age: 24 * 3600, // Keep completed jobs for 24 hours
            count: 1000, // Keep last 1000 completed jobs
        },
        removeOnFail: {
            age: 7 * 24 * 3600, // Keep failed jobs for 7 days
        },
    },
});

// Create worker to process jobs
const worker = new Worker<ScheduleJobData, JobResult>(
    QUEUE_NAME,
    processScheduledPost,
    {
        connection: redisConnection,
        concurrency: parseInt(process.env.MAX_CONCURRENT_JOBS || '10'),
    }
);

// Worker event listeners
worker.on('completed', (job: Job<ScheduleJobData, JobResult>) => {
    console.log(`✅ Job ${job.id} completed successfully for platform: ${job.data.platform}`);
});

worker.on('failed', (job: Job<ScheduleJobData> | undefined, err: Error) => {
    if (job) {
        console.error(`❌ Job ${job.id} failed:`, err.message);
    } else {
        console.error('❌ Job failed:', err.message);
    }
});

worker.on('error', (err: Error) => {
    console.error('⚠️  Worker error:', err);
});

// Queue events for monitoring
const queueEvents = new QueueEvents(QUEUE_NAME, { connection: redisConnection });

queueEvents.on('waiting', ({ jobId }) => {
    console.log(`⏳ Job ${jobId} is waiting`);
});

queueEvents.on('active', ({ jobId }) => {
    console.log(`▶️  Job ${jobId} is now active`);
});

queueEvents.on('progress', ({ jobId, data }) => {
    console.log(`📊 Job ${jobId} progress: ${JSON.stringify(data)}`);
});

// Health check function
export async function getQueueHealth() {
    const [waiting, active, completed, failed, delayed] = await Promise.all([
        schedulerQueue.getWaitingCount(),
        schedulerQueue.getActiveCount(),
        schedulerQueue.getCompletedCount(),
        schedulerQueue.getFailedCount(),
        schedulerQueue.getDelayedCount(),
    ]);

    return {
        waiting,
        active,
        completed,
        failed,
        delayed,
        total: waiting + active + delayed,
    };
}

// Graceful shutdown
export async function shutdownQueue() {
    console.log('🛑 Shutting down scheduler queue...');
    await worker.close();
    await schedulerQueue.close();
    await queueEvents.close();
    await redisConnection.quit();
    console.log('✅ Queue shutdown complete');
}

// Export queue and worker
export { worker };
export default schedulerQueue;
