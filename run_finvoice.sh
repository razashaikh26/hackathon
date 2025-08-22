#!/bin/bash

# FinVoice Production Startup Script
# This script starts the FinVoice backend application with proper environment setup

echo "🚀 Starting FinVoice AI Engine - Production Mode"
echo "================================================"

# Check if virtual environment exists
if [ ! -d "backend/venv" ]; then
    echo "Creating Python virtual environment..."
    cd backend
    python3 -m venv venv
    cd ..
fi

# Activate virtual environment
echo "Activating virtual environment..."
source backend/venv/bin/activate

# Install/upgrade dependencies
echo "Installing/upgrading dependencies..."
cd backend
pip install --upgrade pip
pip install -r requirements.txt

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found!"
    echo "Copying from backend/.env..."
    cp backend/.env .env
fi

# Load environment variables
if [ -f ".env" ]; then
    echo "📝 Loading environment variables from .env file..."
    export $(cat .env | grep -v '^#' | grep -v '^$' | xargs)
fi

# Check if all required environment variables are set
echo "Checking environment configuration..."

required_vars=(
    "DATABASE_URL"
    "VAPI_PRIVATE_KEY"
    "OPENAI_API_KEY"
)

missing_vars=()
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        missing_vars+=("$var")
    fi
done

if [ ${#missing_vars[@]} -gt 0 ]; then
    echo "⚠️  Warning: Missing required environment variables:"
    for var in "${missing_vars[@]}"; do
        echo "   - $var"
    done
    echo ""
    echo "Please set these in your .env file before running in production."
    echo "Starting in demo mode for now..."
    export DEMO_MODE=true
fi

# Start the application
echo "🎯 Starting FinVoice AI Engine..."
echo "   Mode: $(if [ "$DEMO_MODE" = "true" ]; then echo "Demo"; else echo "Production"; fi)"
echo "   Features:"
echo "   - Portfolio computation with live data"
echo "   - Vapi AI voice assistant integration"
echo "   - Blockchain logging (Polygon Amoy)"
echo "   - Multi-language voice support"
echo "   - Real-time financial AI responses"
echo ""
echo "🌐 Application will be available at:"
echo "   - Frontend: http://localhost:3000"
echo "   - Backend API: http://localhost:8000"
echo "   - API Docs: http://localhost:8000/docs"
echo ""

# Run the FastAPI application
if [ "$1" = "dev" ]; then
    echo "🔧 Running in development mode with auto-reload..."
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
else
    echo "🚀 Running in production mode..."
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
fi
