/**
 * Main Express server for scheduler service.
 */
import express, { Express } from 'express';
import cors from 'cors';
import helmet from 'helmet';
import morgan from 'morgan';
import dotenv from 'dotenv';
import scheduleRoutes from './routes/schedule.routes';
import { shutdownQueue } from './queues/scheduler.queue';

// Load environment variables
dotenv.config();

const app: Express = express();
const PORT = process.env.PORT || 3001;

// Middleware
app.use(helmet()); // Security headers
app.use(cors()); // CORS
app.use(morgan('dev')); // Logging
app.use(express.json()); // Body parser
app.use(express.urlencoded({ extended: true }));

// Routes
app.use('/api/v1', scheduleRoutes);

// Root health check
app.get('/', (req, res) => {
    res.json({
        service: 'CaaS Scheduler Service',
        version: '1.0.0',
        status: 'running',
        timestamp: new Date().toISOString(),
    });
});

// 404 handler
app.use((req, res) => {
    res.status(404).json({ error: 'Not found' });
});

// Error handler
app.use((error: Error, req: express.Request, res: express.Response, next: express.NextFunction) => {
    console.error('Server error:', error);
    res.status(500).json({
        error: 'Internal server error',
        message: process.env.NODE_ENV === 'development' ? error.message : undefined
    });
});

// Start server
const server = app.listen(PORT, () => {
    console.log(`\n🚀 Scheduler service running on port ${PORT}`);
    console.log(`📊 Health check: http://localhost:${PORT}/api/v1/health`);
    console.log(`🔧 Environment: ${process.env.NODE_ENV || 'development'}\n`);
});

// Graceful shutdown
process.on('SIGTERM', async () => {
    console.log('\n⚠️  SIGTERM received, shutting down gracefully...');

    server.close(async () => {
        console.log('✅ HTTP server closed');
        await shutdownQueue();
        process.exit(0);
    });

    // Force shutdown after 30 seconds
    setTimeout(() => {
        console.error('❌ Forced shutdown after timeout');
        process.exit(1);
    }, 30000);
});

process.on('SIGINT', async () => {
    console.log('\n⚠️  SIGINT received, shutting down gracefully...');

    server.close(async () => {
        console.log('✅ HTTP server closed');
        await shutdownQueue();
        process.exit(0);
    });
});

// Handle unhandled promise rejections
process.on('unhandledRejection', (reason, promise) => {
    console.error('❌ Unhandled Rejection at:', promise, 'reason:', reason);
});

export default app;
