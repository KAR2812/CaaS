# Content-as-a-Service Platform

A full-stack SaaS application for AI-powered social media content creation and scheduling. Built with Django, Node.js, React, and Next.js.

## What It Does

This platform helps teams create and schedule social media content using AI. Users can generate posts optimized for Twitter, LinkedIn, and Instagram, edit them in a visual editor, and schedule them for publication. The system includes subscription management, team collaboration features, and usage tracking.

## Architecture

The platform uses a microservices approach with four main components:

**Backend API (Django)** - Handles user authentication, content generation via OpenAI/Gemini, subscription billing through Stripe, and data persistence.

**Scheduler Service (Node.js)** - Manages post scheduling using BullMQ, integrates with social media platform APIs, and handles retry logic for failed posts.

**Editor Dashboard (React)** - Provides the main user interface for content creation, editing with drag-and-drop functionality, and schedule management.

**Marketing Site (Next.js)** - Public-facing website with landing pages, pricing information, and documentation.

Supporting infrastructure includes PostgreSQL for data storage and Redis for job queuing and caching.

## Getting Started

The easiest way to run the entire stack locally is with Docker Compose:

```bash
git clone <repository-url>
cd caas

# Set up environment files
cp caas-backend/.env.example caas-backend/.env
cp caas-scheduler/.env.example caas-scheduler/.env

# Add your API keys to the .env files

# Start everything
docker-compose up

# Run database migrations
docker-compose exec django python manage.py migrate
docker-compose exec django python manage.py createsuperuser
```

After starting, you can access:
- Django API at http://localhost:8000
- Scheduler service at http://localhost:3001
- Editor dashboard at http://localhost:5173
- Marketing site at http://localhost:3000

## Configuration

You'll need API keys for the AI providers and Stripe. At minimum, configure these in your `.env` files:

```bash
# Django backend
SECRET_KEY=generate-a-random-key
DATABASE_URL=postgresql://user:pass@localhost:5432/caas
OPENAI_API_KEY=sk-...
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Node.js scheduler
REDIS_URL=redis://localhost:6379
JWT_SECRET=same-as-django-secret
TWITTER_BEARER_TOKEN=optional-for-mvp
LINKEDIN_CLIENT_ID=optional-for-mvp
```

Full configuration details are in the `.env.example` files in each service directory.

## Project Structure

```
caas/
├── caas-backend/          # Django REST API
│   ├── apps/users/        # Authentication and user profiles
│   ├── apps/organizations/# Team workspaces and permissions
│   ├── apps/content/      # Content generation and storage
│   ├── apps/subscriptions/# Stripe integration
│   └── apps/scheduling/   # Post scheduling metadata
│
├── caas-scheduler/        # Node.js scheduling service
│   ├── src/queues/        # BullMQ job processors
│   ├── src/services/      # Social platform integrations
│   └── src/routes/        # REST endpoints
│
├── caas-editor/           # React editor interface
│   ├── src/components/    # UI components
│   └── src/hooks/         # API integration hooks
│
├── caas-marketing/        # Next.js marketing site
│   └── src/app/           # App router pages
│
└── docker-compose.yml     # Development environment
```

## Key Features

**AI Content Generation** - Generates platform-optimized content using OpenAI GPT-4 or Google Gemini. Content is tailored to platform character limits and includes tone selection (professional, casual, educational, etc.).

**Scheduling System** - Queue-based scheduling using BullMQ ensures reliable post delivery. Includes retry logic with exponential backoff and supports scheduling across multiple time zones.

**Subscription Tiers** - Three-tier pricing model integrated with Stripe. Free tier includes 100 tokens/month, Pro tier ($29) gets 5,000 tokens, and Team tier ($99) gets 20,000 tokens. Usage is tracked in real-time.

**Team Collaboration** - Organizations can invite team members with role-based access control. Supports Owner, Admin, Member, and Viewer roles with different permission levels.

**Content Versioning** - Every edit creates a new version, allowing teams to compare iterations and revert changes if needed.

## API Documentation

Interactive documentation is available at http://localhost:8000/api/schema/swagger-ui/ when running locally.

Example request to generate content:

```bash
curl -X POST http://localhost:8000/api/v1/content/generate/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "platform": "twitter",
    "tone": "professional",
    "prompt": "New product launch announcement",
    "organization_id": "org-uuid",
    "ai_provider": "openai"
  }'
```

## Running Tests

```bash
# Backend tests
cd caas-backend
pytest

# Scheduler tests
cd caas-scheduler
npm test

# Editor tests
cd caas-editor
npm test
```

## Deployment Notes

For production deployment, make sure to:

- Set `DEBUG=False` in Django and `NODE_ENV=production` in Node services
- Use production Stripe keys instead of test keys
- Configure ALLOWED_HOSTS and CORS settings appropriately
- Set up SSL/HTTPS termination
- Use managed database services (AWS RDS, DigitalOcean Managed Databases, etc.)
- Use a managed Redis instance (Redis Cloud, AWS ElastiCache)
- Configure error tracking (Sentry, Rollbar)
- Set up proper logging and monitoring
- Use a CDN for static assets

The application works well on platforms like Render, Railway, or AWS ECS. Each service can scale independently.

## Technical Stack

- **Frontend**: React, Next.js, TypeScript, Tailwind CSS
- **Backend**: Django 4.2, Node.js 18+, Express
- **Databases**: PostgreSQL 15, Redis 7
- **Queue System**: BullMQ
- **AI Integration**: OpenAI GPT-4, Google Gemini
- **Payments**: Stripe
- **Social APIs**: Twitter API v2, LinkedIn API, Instagram Graph API

## Why This Architecture?

The Django + Node.js hybrid approach plays to each platform's strengths. Django handles complex business logic, data modeling, and authentication really well. Node.js excels at I/O-heavy operations like API calls to social platforms and benefits from better async handling for job processing.

This separation also means each service can scale independently. The scheduler can handle heavy posting volume without affecting the API, and the API can serve many concurrent users without bottlenecking on outbound social media requests.

## Security

- JWT-based authentication with 15-minute token expiration
- Stripe webhook signature verification
- Rate limiting based on subscription tier
- CORS protection with configurable origins
- HTTPS enforcement in production
- Django ORM prevents SQL injection
- React sanitization prevents XSS attacks

## Troubleshooting

**Services won't start**: Check that ports 3000, 3001, 5173, 8000, 5432, and 6379 aren't already in use. Run `docker-compose ps` to see service status.

**Database errors**: Try `docker-compose exec django python manage.py migrate --run-syncdb` to rebuild the schema.

**Redis connection fails**: Test with `docker-compose exec redis redis-cli ping` - should return "PONG".

**AI generation fails**: Verify your API keys are correctly set in the `.env` file and that you have quota available with OpenAI/Gemini.

## License

MIT License - see the LICENSE file for details.

## Questions?

Each service has its own README with detailed setup instructions:
- [Django Backend](./caas-backend/README.md)
- [Node.js Scheduler](./caas-scheduler/README.md)
- [React Editor](./caas-editor/README.md)
- [Next.js Marketing](./caas-marketing/README.md)
