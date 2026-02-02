#!/bin/bash
# Quick start script for local development

echo "🚀 Starting CaaS Platform..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop."
    exit 1
fi

# Check if .env files exist
if [ ! -f caas-backend/.env ]; then
    echo "📝 Creating caas-backend/.env from example..."
    cp caas-backend/.env.example caas-backend/.env
    echo "⚠️  Please edit caas-backend/.env with your API keys"
fi

if [ ! -f caas-scheduler/.env ]; then
    echo "📝 Creating caas-scheduler/.env from example..."
    cp caas-scheduler/.env.example caas-scheduler/.env
    echo "⚠️  Please edit caas-scheduler/.env with your API keys"
fi

# Start services
echo "🐳 Starting Docker Compose..."
docker-compose up -d postgres redis

# Wait for databases
echo "⏳ Waiting for databases to be ready..."
sleep 5

# Start Django
echo "🐍 Starting Django backend..."
docker-compose up -d django

# Wait for Django to start
sleep 3

# Run migrations
echo "📊 Running database migrations..."
docker-compose exec -T django python manage.py migrate

# Load initial data
echo "📦 Loading subscription plans..."
docker-compose exec -T django python manage.py loaddata apps/subscriptions/fixtures/plans.json || true

# Create superuser (optional, skip if exists)
echo ""
echo "👤 Create Django superuser (optional, Ctrl+C to skip):"
docker-compose exec django python manage.py createsuperuser || true

# Start remaining services
echo "🚀 Starting remaining services..."
docker-compose up -d

echo ""
echo "✅ CaaS Platform is ready!"
echo ""
echo "🌐 Services available at:"
echo "   Django API:    http://localhost:8000"
echo "   API Docs:      http://localhost:8000/api/schema/swagger-ui/"
echo "   Scheduler:     http://localhost:3001"
echo "   Scheduler Health: http://localhost:3001/api/v1/health"
echo ""
echo "📊 View logs with: docker-compose logs -f"
echo "🛑 Stop with: docker-compose down"
