# 🚀 CaaS Platform - Ready to Run Checklist

## Prerequisites Verification

### Required Software
- [ ] Docker Desktop installed and running
- [ ] OR: Python 3.11+, Node.js 18+, PostgreSQL 15+, Redis 7+

### API Keys (Optional for initial testing)
- [ ] OpenAI API key (`OPENAI_API_KEY`)
- [ ] OR Google Gemini API key (`GEMINI_API_KEY`)
- [ ] Stripe test keys (`STRIPE_SECRET_KEY`, `STRIPE_PUBLISHABLE_KEY`)
- [ ] Stripe webhook secret (`STRIPE_WEBHOOK_SECRET`)

## Quick Start with Docker

### 1. Initial Setup (First Time Only)
```bash
cd caas

# Copy environment files
cp caas-backend/.env.example caas-backend/.env
cp caas-scheduler/.env.example caas-scheduler/.env

# Edit .env files with your API keys (optional for testing)
# At minimum, set:
# - DATABASE_URL (already set for Docker)
# - REDIS_URL (already set for Docker)
# - JWT_SECRET_KEY (generate a random string)
```

### 2. Start Everything
```bash
# Option A: Use start script (recommended)
./start.sh

# Option B: Manual start
docker-compose up -d postgres redis
sleep 5
docker-compose up -d django
docker-compose exec django python manage.py migrate
docker-compose exec django python manage.py loaddata apps/subscriptions/fixtures/plans.json
docker-compose exec django python manage.py createsuperuser
docker-compose up -d
```

### 3. Verify Services

#### Check all services are running:
```bash
docker-compose ps

# Should show:
# - caas-postgres (healthy)
# - caas-redis (healthy)
# - caas-django (healthy)
# - caas-scheduler (healthy)
```

#### Test Django API:
```bash
curl http://localhost:8000/api/schema/

# Should return OpenAPI schema JSON
```

#### Test Scheduler:
```bash
curl http://localhost:3001/api/v1/health

# Should return: {"status":"healthy","service":"scheduler",...}
```

#### Open Swagger UI:
```bash
open http://localhost:8000/api/schema/swagger-ui/
```

## File Structure Verification

### Django Backend
```
caas-backend/
├── apps/
│   ├── users/
│   │   ├── models.py ✓
│   │   ├── views.py ✓
│   │   ├── serializers.py ✓
│   │   ├── urls.py ✓
│   │   └── migrations/__init__.py ✓
│   ├── organizations/ (same structure) ✓
│   ├── content/ (same structure) ✓
│   ├── subscriptions/
│   │   └── fixtures/plans.json ✓
│   └── scheduling/ ✓
├── config/
│   ├── settings/
│   │   ├── base.py ✓
│   │   ├── development.py ✓
│   │   └── production.py ✓
│   ├── urls.py ✓
│   └── wsgi.py ✓
├── manage.py ✓
├── requirements.txt ✓
├── .env.example ✓
├── .gitignore ✓
└── Dockerfile ✓
```

### Node.js Scheduler
```
caas-scheduler/
├── src/
│   ├── index.ts ✓
│   ├── config/redis.ts ✓
│   ├── queues/
│   │   ├── scheduler.queue.ts ✓
│   │   └── processor.ts ✓
│   ├── services/
│   │   ├── django-client.ts ✓
│   │   └── platforms/
│   │       ├── base.platform.ts ✓
│   │       ├── twitter.platform.ts ✓
│   │       ├── linkedin.platform.ts ✓
│   │       └── instagram.platform.ts ✓
│   ├── routes/schedule.routes.ts ✓
│   ├── middleware/auth.middleware.ts ✓
│   └── types/index.ts ✓
├── package.json ✓
├── tsconfig.json ✓
├── .env.example ✓
├── .gitignore ✓
└── Dockerfile ✓
```

## Environment Variables Checklist

### Django (caas-backend/.env)
```bash
# Required
DEBUG=True
SECRET_KEY=your-secret-key-here-generate-with-python-secrets
DATABASE_URL=postgresql://caas:dev_password@localhost:5432/caas_db
REDIS_URL=redis://localhost:6379/0
JWT_SECRET_KEY=your-jwt-secret-shared-with-nodejs

# AI Providers (at least one)
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=...

# Stripe (optional for testing)
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...

# Frontend URLs (for CORS)
FRONTEND_EDITOR_URL=http://localhost:5173
FRONTEND_MARKETING_URL=http://localhost:3000
```

### Node.js (caas-scheduler/.env)
```bash
# Required
NODE_ENV=development
PORT=3001
REDIS_URL=redis://localhost:6379
DJANGO_API_URL=http://localhost:8000
JWT_SECRET=your-jwt-secret-shared-with-django
SERVICE_TOKEN=shared-service-secret-token

# Social Platform APIs (optional for testing)
TWITTER_BEARER_TOKEN=...
LINKEDIN_CLIENT_ID=...
LINKEDIN_CLIENT_SECRET=...
```

## Testing the Platform

### 1. Access Django Admin
```bash
# Open admin panel
open http://localhost:8000/admin/

# Login with superuser credentials created earlier
# You should see: Users, Organizations, Content, Subscriptions, Scheduled Posts
```

### 2. Test API via Swagger
```bash
# Open Swagger UI
open http://localhost:8000/api/schema/swagger-ui/

# Try these endpoints:
# 1. POST /api/v1/auth/register/ - Register a user
# 2. POST /api/v1/auth/login/ - Login (get JWT token)
# 3. Use "Authorize" button and paste JWT token
# 4. POST /api/v1/content/generate/ - Generate AI content
```

### 3. Test with cURL

#### Register a user:
```bash
curl -X POST http://localhost:8000/api/v1/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpass123",
    "first_name": "Test",
    "last_name": "User"
  }'
```

#### Login:
```bash
TOKEN=$(curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpass123"}' \
  | jq -r '.access')

echo "Token: $TOKEN"
```

#### Create Organization:
```bash
ORG_ID=$(curl -X POST http://localhost:8000/api/v1/organizations/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"My Company","description":"Test organization"}' \
  | jq -r '.id')

echo "Organization ID: $ORG_ID"
```

#### Generate AI Content (requires OpenAI/Gemini key):
```bash
curl -X POST http://localhost:8000/api/v1/content/generate/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "platform": "twitter",
    "tone": "professional",
    "prompt": "Announce our new AI-powered content platform",
    "audience": "tech professionals",
    "organization_id": "'$ORG_ID'",
    "ai_provider": "openai"
  }'
```

#### Check Subscription Plans:
```bash
curl -X GET http://localhost:8000/api/v1/subscriptions/plans/ \
  -H "Authorization: Bearer $TOKEN"

# Should return Free, Pro, and Team plans
```

## Common Issues & Solutions

### Issue: "Connection refused" errors

**Solution:**
```bash
# Check services are running
docker-compose ps

# Restart services
docker-compose restart
```

### Issue: "Migrations not applied"

**Solution:**
```bash
docker-compose exec django python manage.py migrate
```

### Issue: "No such file: .env"

**Solution:**
```bash
cp caas-backend/.env.example caas-backend/.env
cp caas-scheduler/.env.example caas-scheduler/.env
```

### Issue: "Port already in use"

**Solution:**
```bash
# Find and kill process using port
lsof -ti:8000 | xargs kill -9
lsof -ti:3001 | xargs kill -9

# Or change ports in docker-compose.yml
```

### Issue: "Database connection failed"

**Solution:**
```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Check DATABASE_URL in .env
# Should be: postgresql://caas:dev_password@postgres:5432/caas_db (for Docker)
# Or: postgresql://caas:dev_password@localhost:5432/caas_db (for local)
```

### Issue: "Redis connection failed"

**Solution:**
```bash
# Check Redis is running
docker-compose ps redis

# Test Redis connection
docker-compose exec redis redis-cli ping
# Should return: PONG
```

## Production Deployment

Before deploying to production:

1. **Security**
   - [ ] Set `DEBUG=False`
   - [ ] Generate strong `SECRET_KEY` and `JWT_SECRET`
   - [ ] Use production database (managed PostgreSQL)
   - [ ] Use production Redis (managed service)
   - [ ] Configure `ALLOWED_HOSTS`
   - [ ] Set up HTTPS/SSL
   - [ ] Switch Stripe to live mode

2. **Performance**
   - [ ] Collect static files: `python manage.py collectstatic`
   - [ ] Use Gunicorn/uWSGI for Django
   - [ ] Use PM2 for Node.js
   - [ ] Set up CDN for assets
   - [ ] Configure database connection pooling

3. **Monitoring**
   - [ ] Set up error tracking (Sentry)
   - [ ] Configure logging
   - [ ] Set up health checks
   - [ ] Configure monitoring (DataDog, New Relic)

See [README.md](README.md) for detailed deployment guides.

## Quick Command Reference

```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# View logs
docker-compose logs -f

# Run Django commands
docker-compose exec django python manage.py <command>

# Run Node.js commands
docker-compose exec scheduler npm run <command>

# Restart a service
docker-compose restart django

# Rebuild after code changes
docker-compose up -d --build
```

## Documentation

- Main README: [README.md](README.md)
- Manual Setup: [SETUP.md](SETUP.md)
- Quick Reference: [QUICKREF.md](QUICKREF.md)
- Django Backend: [caas-backend/README.md](caas-backend/README.md)
- Node.js Scheduler: [caas-scheduler/README.md](caas-scheduler/README.md)
- Implementation Walkthrough: [.gemini/antigravity/brain/*/walkthrough.md]

## Support

If you encounter issues:
1. Check logs: `docker-compose logs -f`
2. Verify .env files are configured
3. Ensure all services are healthy: `docker-compose ps`
4. Review [SETUP.md](SETUP.md) for troubleshooting

---

✅ **Project is ready to run!**

Start with: `./start.sh` or `docker-compose up`
