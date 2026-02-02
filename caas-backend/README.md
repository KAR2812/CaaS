# CaaS Backend - Django Core Service

Production-grade Django backend for the AI-Powered Content-as-a-Service (CaaS) platform.

## 🏗️ Architecture

This Django service handles:
- **Authentication & Authorization** (JWT with djangorestframework-simplejwt)
- **Multi-tenancy** (Organizations, Workspaces, RBAC)
-  **AI Content Generation** (OpenAI GPT-4 & Google Gemini integration)
- **Subscription Management** (Stripe billing & webhooks)
- **Scheduling Coordination** (HTTP client for Node.js scheduler service)

## 📁 Project Structure

```
caas-backend/
├── config/                    # Django project configuration
│   ├── settings/
│   │   ├── base.py           # Shared settings
│   │   ├── development.py    # Dev environment
│   │   └── production.py     # Prod environment
│   ├── urls.py               # URL routing
│   ├── wsgi.py              # WSGI entry point
│   └── asgi.py              # ASGI entry point
├── apps/
│   ├── users/               # Custom User, JWT auth, profiles
│   ├── organizations/       # Multi-tenancy, workspaces, RBAC
│   ├── content/            # AI content generation, versioning
│   ├── subscriptions/      # Stripe plans, billing, webhooks
│   └── scheduling/         # Metadata for scheduled posts
├── manage.py
├── requirements.txt
└── .env.example
```

## 🚀 Quick Start

### 1. Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Redis 7+ (for caching & coordination)

### 2. Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Edit .env with your credentials (see Configuration section)
```

### 3. Database Setup

```bash
# Create PostgreSQL database
createdb caas_db

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Load initial subscription plans (optional)
python manage.py loaddata fixtures/plans.json
```

### 4. Run Development Server

```bash
# Make sure PostgreSQL and Redis are running
python manage.py runserver
```

Server runs at `http://localhost:8000`

## ⚙️ Configuration

### Required Environment Variables

```bash
# Django
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_URL=postgresql://caas:dev_password@localhost:5432/caas_db

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT
JWT_SECRET_KEY=your-jwt-secret-shared-with-nodejs
JWT_ACCESS_TOKEN_LIFETIME=15  # minutes
JWT_REFRESH_TOKEN_LIFETIME=10080  # 7 days

# Stripe
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_PRICE_ID_PRO=price_...
STRIPE_PRICE_ID_TEAM=price_...

# OpenAI
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4-turbo-preview

# Google Gemini
GEMINI_API_KEY=...
GEMINI_MODEL=gemini-1.5-pro

# Node.js Scheduler Service
SCHEDULER_SERVICE_URL=http://localhost:3001
SCHEDULER_SERVICE_TOKEN=shared-secret-token

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
```

## 📡 API Endpoints

### Authentication
- `POST /api/v1/auth/register/` - User registration
- `POST /api/v1/auth/login/` - Login (returns JWT tokens)
- `POST /api/v1/auth/token/refresh/` - Refresh access token
- `POST /api/v1/auth/logout/` - Logout (blacklist refresh token)
- `GET /api/v1/auth/profile/` - Get/update user profile

### Organizations
- `GET /api/v1/organizations/` - List user's organizations
- `POST /api/v1/organizations/` - Create organization
- `GET /api/v1/organizations/{id}/members/` - List members
- `POST /api/v1/organizations/workspaces/` - Create workspace

### Content (AI Generation)
- `POST /api/v1/content/generate/` - Generate AI content
- `POST /api/v1/content/{id}/regenerate/` - Regenerate with modifications
- `GET /api/v1/content/` - List organization's content
- `GET /api/v1/content/{id}/` - Get content detail
- `GET /api/v1/content/{id}/versions/` - Get version history

### Subscriptions
- `GET /api/v1/subscriptions/plans/` - List available plans
- `POST /api/v1/subscriptions/create-checkout-session/` - Start Stripe checkout
- `GET /api/v1/subscriptions/` - Get organization subscription
- `POST /api/v1/subscriptions/webhook/` - Stripe webhook handler

### Scheduling
- `POST /api/v1/scheduling/schedule/` - Schedule a post
- `POST /api/v1/scheduling/{id}/cancel/` - Cancel scheduled post
- `GET /api/v1/scheduling/` - List scheduled posts
- `POST /api/v1/scheduling/callback/` - Callback from Node.js service

### API Documentation
- `/api/schema/` - OpenAPI schema (JSON)
- `/api/schema/swagger-ui/` - Interactive Swagger UI

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=apps --cov-report=html

# Run specific app tests
pytest apps/users/tests/
pytest apps/content/tests/

# Run linting
flake8 apps/
black apps/ --check
```

## 🔐 Security Features

- **JWT Authentication** with short-lived access tokens (15 min)
- **Rate Limiting** per subscription tier
- **CORS** configured for frontend origins
- **Stripe Webhook Verification** for billing events
- **HTTPS-only** in production (enforced in settings)
- **CSRF Protection** for non-API endpoints
- **SQL Injection Protection** via Django ORM
- **Password Validation** with Django validators

## 🎯 Key Features

### AI Content Generation
```python
# Example: Generate content
POST /api/v1/content/generate/
{
    "platform": "twitter",
    "tone": "professional",
    "prompt": "Announce our new product launch",
    "audience": "tech enthusiasts",
    "organization_id": "uuid",
    "ai_provider": "openai"
}

Response:
{
    "id": "uuid",
    "generated_text": "🚀 Exciting news! We're launching...",
    "tokens_used": 125,
    "version": 1
}
```

### Subscription Tiers
| Tier | Price | Tokens/mo | Posts | Workspaces | Members |
|------|-------|-----------|-------|------------|---------|
| Free | $0 | 100 | 5 | 1 | 1 |
| Pro | $29 | 5,000 | 100 | 3 | 1 |
| Team | $99 | 20,000 | Unlimited | 10 | 10 |

## 🔄 Service-to-Service Communication

Django communicates with the Node.js scheduler via HTTP:

```python
# Schedule a post
SchedulerClient.schedule_post(
    content_id=content.id,
    platform='twitter',
    scheduled_at='2026-02-15T10:00:00Z',
    user=request.user,
    org_id=org.id
)
```

Node.js sends callbacks on job completion:
```
POST /api/v1/scheduling/callback/
{
    "job_id": "bull_job_123",
    "content_id": "uuid",
    "status": "published",
    "platform_post_id": "12345"
}
```

## 📦 Database Models

### Key Relationships
```
User (1) ──→ (N) OrganizationMember ──→ (1) Organization
Organization (1) ──→ (1) Subscription ──→ (1) Plan
Organization (1) ──→ (N) Workspace
Organization (1) ──→ (N) Content ──→ (N) ContentVersion
Content (1) ──→ (N) ScheduledPost
```

## 🚀 Deployment

### Production Checklist

1. Set `DEBUG=False`
2. Use strong `SECRET_KEY` and `JWT_SECRET_KEY`
3. Configure `ALLOWED_HOSTS`
4. Set up PostgreSQL with connection pooling
5. Configure Redis for caching
6. Set all Stripe keys to production mode
7. Enable HTTPS enforcement
8. Set up error logging (Sentry recommended)
9. Run `python manage.py collectstatic`
10. Use Gunicorn as WSGI server

### Using Gunicorn

```bash
# Install
pip install gunicorn

# Run
gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 4
```

### Docker Deployment

```bash
# Build
docker build -t caas-backend .

# Run
docker run -p 8000:8000 --env-file .env caas-backend
```

## 🔧 Development Commands

```bash
# Create new app
python manage.py startapp app_name apps/

# Make migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create admin user
python manage.py createsuperuser

# Shell with Django context
python manage.py shell_plus  # requires django-extensions

# Database shell
python manage.py dbshell
```

## 🐛 Troubleshooting

### Common Issues

**Database connection errors:**
```bash
# Check PostgreSQL is running
pg_isready

# Test connection
psql -U caas -d caas_db
```

**Redis connection errors:**
```bash
# Check Redis is running
redis-cli ping

# Should return: PONG
```

**Migration conflicts:**
```bash
# Reset migrations (DEV ONLY!)
python manage.py migrate app_name zero
python manage.py makemigrations
python manage.py migrate
```

## 📚 Additional Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Stripe API Docs](https://stripe.com/docs/api)
- [OpenAI API](https://platform.openai.com/docs)
- [Google Gemini API](https://ai.google.dev/docs)

## 🏆 Interview Talking Points

### Why Django?
- **Mature ecosystem** for business logic and CRUD operations
- **Built-in admin panel** for ops team
- **Strong ORM** for complex database relationships
- **Security by default** (CSRF, SQL injection protection)
- **Excellent for transactional workloads**

### Architecture Decisions
- **Hybrid backend**: Django for business logic, Node.js for I/O-heavy scheduling
- **JWT over sessions**: Stateless auth for microservices compatibility
- **PostgreSQL**: ACID compliance for billing, multi-tenancy support
- **Redis**: Distributed caching and service coordination

### Scalability
- **Horizontal scaling**: Stateless design allows multiple Django instances
- **Read replicas**: PostgreSQL read replicas for analytics queries
- **Caching layers**: Redis for frequently accessed data
- **Async offloading**: Heavy operations delegated to Node.js service

---

**License**: MIT
**Maintainer**: CaaS Platform Team
