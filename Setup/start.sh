#!/bin/bash

# Dynamic Pricing Engine - Quick Start Script

set -e

echo "🚀 Starting Dynamic Pricing Engine Setup..."
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create environment files if they don't exist
if [ ! -f "dpe-backend/.env" ]; then
    echo "📝 Creating backend .env file..."
    cp dpe-backend/.env.example dpe-backend/.env
fi

if [ ! -f "dpe-frontend/.env.local" ]; then
    echo "📝 Creating frontend .env.local file..."
    cp dpe-frontend/.env.local.example dpe-frontend/.env.local
fi

# Start services
echo "🐳 Starting Docker containers..."
docker-compose up -d

# Wait for services to be healthy
echo "⏳ Waiting for services to start..."
sleep 10

# Run migrations
echo "📊 Running database migrations..."
docker-compose exec -T backend alembic upgrade head

echo ""
echo "✅ Setup complete!"
echo ""
echo "📍 Services are running at:"
echo "   - Frontend:  http://localhost:3000"
echo "   - Backend:   http://localhost:8000"
echo "   - API Docs:  http://localhost:8000/api/v1/docs"
echo ""
echo "🎯 Next steps:"
echo "   1. Open http://localhost:3000 in your browser"
echo "   2. Register a new account"
echo "   3. Start creating products and optimizing prices!"
echo ""
echo "📝 To view logs:"
echo "   docker-compose logs -f"
echo ""
echo "🛑 To stop services:"
echo "   docker-compose down"
echo ""
