# Manual Setup Guide (Without Docker)

If you prefer to run services manually without Docker, follow these steps:

## Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Redis 7+

## 1. Database Setup

### PostgreSQL
```bash
# Install PostgreSQL (macOS)
brew install postgresql@15
brew services start postgresql@15

# Create database and user
createdb caas_db
psql -d caas_db -c "CREATE USER caas WITH PASSWORD 'dev_password';"
psql -d caas_db -c "GRANT ALL PRIVILEGES ON DATABASE caas_db TO caas;"
```

### Redis
```bash
# Install Redis (macOS)
brew install redis
brew services start redis

# Verify
redis-cli ping  # Should return PONG
```

## 2. Django Backend

```bash
cd caas-backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Edit .env with your configuration:
# - DATABASE_URL=postgresql://caas:dev_password@localhost:5432/caas_db
# - OPENAI_API_KEY=your-key
# - STRIPE_SECRET_KEY=your-key
# - etc.

# Run migrations
python manage.py migrate

# Load initial subscription plans
python manage.py loaddata apps/subscriptions/fixtures/plans.json

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

Django API will be available at: http://localhost:8000

## 3. Node.js Scheduler

```bash
cd caas-scheduler

# Install dependencies
npm install

# Create .env file
cp .env.example .env

# Edit .env with your configuration:
# - REDIS_URL=redis://localhost:6379
# - DJANGO_API_URL=http://localhost:8000
# - JWT_SECRET=same-as-django
# - TWITTER_BEARER_TOKEN=your-token
# - etc.

# Run in development mode
npm run dev
```

Scheduler will be available at: http://localhost:3001

## 4. Verify Services

### Django API
```bash
# Health check
curl http://localhost:8000/api/schema/

# API documentation
open http://localhost:8000/api/schema/swagger-ui/
```

### Scheduler
```bash
# Health check
curl http://localhost:3001/api/v1/health

# Should return:
# {"status":"healthy","service":"scheduler","queue":{...}}
```

## 5. Test the Stack

### Register a user
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

### Login
```bash
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpass123"
  }'

# Save the access token from response
```

### Generate AI content
```bash
curl -X POST http://localhost:8000/api/v1/content/generate/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "platform": "twitter",
    "tone": "professional",
    "prompt": "Announce a new AI feature",
    "audience": "tech professionals",
    "ai_provider": "openai"
  }'
```

## Troubleshooting

### Django Issues

**ImportError for apps**:
- Make sure all `__init__.py` files exist in app directories
- Check `INSTALLED_APPS` in settings

**Database connection errors**:
```bash
# Test connection
psql -U caas -d caas_db -h localhost

# If password auth fails, check pg_hba.conf
```

**Missing dependencies**:
```bash
pip install -r requirements.txt --upgrade
```

### Node.js Issues

**Redis connection errors**:
```bash
# Check Redis is running
redis-cli ping

# Check REDIS_URL in .env
```

**TypeScript errors**:
```bash
# Rebuild
npm run build

# Check types
npx tsc --noEmit
```

### Common Issues

**Port already in use**:
```bash
# Find process using port 8000
lsof -ti:8000

# Kill process
kill -9 <PID>
```

**Permission denied on start.sh**:
```bash
chmod +x start.sh
```

## Running Tests

### Django
```bash
cd caas-backend
source venv/bin/activate
pytest
```

### Node.js
```bash
cd caas-scheduler
npm test
```

## Production Deployment

See main [README.md](../README.md) for production deployment guides.
