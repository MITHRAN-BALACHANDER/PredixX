#!/bin/bash

# Test Model Integration Script

echo "=================================="
echo "Testing Model Integration"
echo "=================================="
echo ""

# Check if Docker is running
if ! docker-compose ps | grep -q "dpe-backend"; then
    echo "❌ Backend container not running"
    echo "Start with: docker-compose up -d"
    exit 1
fi

echo "✓ Backend container is running"
echo ""

# Check model files
echo "Checking model files in container..."
docker-compose exec backend ls -lh /app/models/

echo ""
echo "Running model verification..."
docker-compose exec backend python verify_models.py

echo ""
echo "=================================="
echo "Test Complete!"
echo "=================================="
