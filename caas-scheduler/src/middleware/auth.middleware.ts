/**
 * JWT authentication middleware.
 */
import { Request, Response, NextFunction } from 'express';
import jwt from 'jsonwebtoken';
import { AuthenticatedRequest } from '../types';

const JWT_SECRET = process.env.JWT_SECRET || 'your-secret-key';
const SERVICE_TOKEN = process.env.SERVICE_TOKEN || '';

/**
 * Middleware to verify JWT token from Django.
 */
export function authenticateJWT(
    req: Request,
    res: Response,
    next: NextFunction
): void {
    const authHeader = req.headers.authorization;
    const serviceToken = req.headers['x-service-token'];

    // Allow service-to-service calls with service token
    if (serviceToken && serviceToken === SERVICE_TOKEN) {
        return next();
    }

    // Verify JWT token
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
        res.status(401).json({ error: 'Missing or invalid authorization header' });
        return;
    }

    const token = authHeader.substring(7);

    try {
        const decoded = jwt.verify(token, JWT_SECRET) as { user_id: string; email: string };
        (req as AuthenticatedRequest).user = {
            id: decoded.user_id,
            email: decoded.email,
        };
        next();
    } catch (error) {
        res.status(403).json({ error: 'Invalid or expired token' });
    }
}
