#!/bin/bash

# FinVoice Backend Setup with Cloud Services
# No local PostgreSQL or Redis installation required!

echo "🚀 Setting up FinVoice Backend with Cloud Services"
echo "=================================================="

# Check if we're in the correct directory
if [ ! -f "requirements.txt" ]; then
    echo "❌ Please run this script from the backend directory"
    exit 1
fi

echo "📋 Step 1: Python Virtual Environment"
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

echo ""
echo "📋 Step 2: Activate Virtual Environment"
echo "Run: source venv/bin/activate"

echo ""
echo "📋 Step 3: Install Dependencies"
echo "Run: pip install -r requirements.txt"

echo ""
echo "📋 Step 4: Set up Cloud Databases"
echo "1. Neon Database (PostgreSQL): https://neon.tech/"
echo "   - Sign up (free)"
echo "   - Create project 'finvoice'"
echo "   - Enable pgvector: CREATE EXTENSION IF NOT EXISTS vector;"
echo "   - Copy connection string to .env"
echo ""
echo "2. Upstash Redis: https://upstash.com/"
echo "   - Sign up (free)"
echo "   - Create Redis database"
echo "   - Copy Redis URL to .env"

echo ""
echo "📋 Step 5: Update .env file"
echo "Replace these placeholders in .env:"
echo "DATABASE_URL=postgresql://your_username:your_password@ep-xyz.region.neon.tech/neondb?sslmode=require"
echo "REDIS_URL=rediss://default:your_password@region.upstash.io:6379"

echo ""
echo "📋 Step 6: Run Database Migrations"
echo "Run: alembic upgrade head"

echo ""
echo "📋 Step 7: Start Backend Server"
echo "Run: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

echo ""
echo "🎉 No local installations needed!"
echo "✅ Database: Neon (cloud PostgreSQL)"
echo "✅ Cache: Upstash (cloud Redis)"
echo "✅ Backend: FastAPI (Python)"

echo ""
echo "📱 After setup, your APIs will be available at:"
echo "- Backend: http://localhost:8000"
echo "- API Docs: http://localhost:8000/docs"
echo "- Health Check: http://localhost:8000/health"
