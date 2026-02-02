/**
 * Redis configuration for BullMQ and caching.
 */
import { Redis } from 'ioredis';
import dotenv from 'dotenv';

dotenv.config();

// Create Redis connection for BullMQ
export const redisConnection = new Redis(process.env.REDIS_URL || 'redis://localhost:6379');

// Test connection
redisConnection.on('connect', () => {
    console.log('✅ Redis connected successfully');
});

redisConnection.on('error', (err) => {
    console.error('❌ Redis connection error:', err);
});

export default redisConnection;
