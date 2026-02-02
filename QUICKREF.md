# Quick Reference: Essential Commands

## Docker Commands

```bash
# Start all services
docker-compose up

# Start in background
docker-compose up -d

# Stop all services
docker-compose down

# View logs
docker-compose logs -f
docker-compose logs -f django
docker-compose logs -f scheduler

# Restart a service
docker-compose restart django

# Rebuild after code changes
docker-compose up -d --build

# Execute commands in containers
docker-compose exec django python manage.py migrate
docker-compose exec django python manage.py createsuperuser
docker-compose exec scheduler npm run build

# Clean everything (WARNING: deletes data)
docker-compose down -v
```

## Django Management Commands

```bash
# Run migrations
python manage.py migrate

# Create migrations
python manage.py makemigrations

# Create superuser
python manage.py createsuperuser

# Load fixtures
python manage.py loaddata apps/subscriptions/fixtures/plans.json

# Django shell
python manage.py shell

# Collect static files (production)
python manage.py collectstatic

# Database shell
python manage.py dbshell

# Run development server
python manage.py runserver
```

## API Endpoints Quick Reference

### Authentication
```bash
POST   /api/v1/auth/register/         # Register user
POST   /api/v1/auth/login/            # Login (get JWT)
POST   /api/v1/auth/token/refresh/    # Refresh token
POST   /api/v1/auth/logout/           # Logout
GET    /api/v1/auth/profile/          # Get profile
```

### Content Generation
```bash
POST   /api/v1/content/generate/      # Generate AI content
POST   /api/v1/content/{id}/regenerate/ # Regenerate
GET    /api/v1/content/               # List content
GET    /api/v1/content/{id}/          # Get content
GET    /api/v1/content/{id}/versions/ # Version history
```

### Organizations
```bash
GET    /api/v1/organizations/         # List orgs
POST   /api/v1/organizations/         # Create org
GET    /api/v1/organizations/{id}/members/ # List members
POST   /api/v1/organizations/workspaces/   # Create workspace
```

### Subscriptions
```bash
GET    /api/v1/subscriptions/plans/   # List plans
POST   /api/v1/subscriptions/create-checkout-session/ # Stripe checkout
GET    /api/v1/subscriptions/         # Get subscription
POST   /api/v1/subscriptions/webhook/ # Stripe webhook
```

### Scheduling (Node.js)
```bash
POST   /api/v1/schedule               # Schedule post
GET    /api/v1/schedule/{jobId}       # Get job status
DELETE /api/v1/schedule/{jobId}       # Cancel job
GET    /api/v1/health                 # Queue health
```

## Environment Variables Checklist

### Django (.env)
- [ ] SECRET_KEY
- [ ] DATABASE_URL
- [ ] REDIS_URL
- [ ] OPENAI_API_KEY
- [ ] GEMINI_API_KEY
- [ ] STRIPE_SECRET_KEY
- [ ] STRIPE_PUBLISHABLE_KEY
- [ ] STRIPE_WEBHOOK_SECRET
- [ ] JWT_SECRET_KEY

### Node.js (.env)
- [ ] REDIS_URL
- [ ] DJANGO_API_URL
- [ ] JWT_SECRET (same as Django)
- [ ] SERVICE_TOKEN
- [ ] TWITTER_BEARER_TOKEN
- [ ] LINKEDIN_CLIENT_ID
- [ ] LINKEDIN_CLIENT_SECRET

## URLs

- Main README: http://localhost:8000/
- Django Admin: http://localhost:8000/admin/
- Swagger UI: http://localhost:8000/api/schema/swagger-ui/
- OpenAPI Schema: http://localhost:8000/api/schema/
- Scheduler Health: http://localhost:3001/api/v1/health

## Testing Flows

### 1. Register → Login → Generate Content
```bash
# 1. Register
curl -X POST http://localhost:8000/api/v1/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"email":"user@test.com","password":"pass123","first_name":"John","last_name":"Doe"}'

# 2. Login
TOKEN=$(curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"user@test.com","password":"pass123"}' | jq -r '.access')

# 3. Generate Content
curl -X POST http://localhost:8000/api/v1/content/generate/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"platform":"twitter","tone":"casual","prompt":"Hello world","ai_provider":"openai"}'
```

### 2. Create Organization → Workspace
```bash
# Create org (use token from above)
ORG_ID=$(curl -X POST http://localhost:8000/api/v1/organizations/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"My Company","description":"Test org"}' | jq -r '.id')

# Create workspace
curl -X POST http://localhost:8000/api/v1/organizations/workspaces/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"organization":"'$ORG_ID'","name":"Marketing"}'
```

## Troubleshooting

### Reset Database
```bash
docker-compose down -v
docker-compose up -d postgres redis
docker-compose up -d django
docker-compose exec django python manage.py migrate
docker-compose exec django python manage.py loaddata apps/subscriptions/fixtures/plans.json
```

### View Redis Queue
```bash
docker-compose exec redis redis-cli
> KEYS *
> GET bull:social-posts:*
```

### Check Logs
```bash
# All services
docker-compose logs --tail=100 -f

# Specific service
docker-compose logs --tail=50 -f django
docker-compose logs --tail=50 -f scheduler
```
