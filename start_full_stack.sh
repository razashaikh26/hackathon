#!/bin/bash

# FinVoice Full Stack Startup Script
# Starts both backend (Python FastAPI) and frontend (React)

echo "🚀 Starting FinVoice Full Stack Application..."
echo "================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Kill any existing processes on our ports
echo "🧹 Cleaning up existing processes..."
if lsof -ti:8000 > /dev/null 2>&1; then
    print_warning "Killing existing backend server on port 8000..."
    lsof -ti:8000 | xargs kill -9
    sleep 2
fi

if lsof -ti:3000 > /dev/null 2>&1; then
    print_warning "Killing existing frontend server on port 3000..."
    lsof -ti:3000 | xargs kill -9
    sleep 2
fi

# Start Backend
echo ""
echo "🐍 Starting Backend (FastAPI)..."
echo "--------------------------------"
cd "/Users/razashaikh/Desktop/final ro/backend/app"

# Check if virtual environment needs to be activated
if [ ! -f "basic_main.py" ]; then
    print_error "Backend files not found!"
    exit 1
fi

print_info "Starting backend server in background..."
nohup /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 basic_main.py > ../backend.log 2>&1 &
BACKEND_PID=$!

print_info "Backend started with PID: $BACKEND_PID"
print_info "Waiting for backend to initialize..."

# Wait for backend to start
sleep 8

# Check if backend is running
if curl -s http://localhost:8000/ > /dev/null; then
    print_status "Backend is running successfully!"
    print_info "Backend API: http://localhost:8000"
    print_info "API Documentation: http://localhost:8000/docs"
    print_info "Backend logs: tail -f backend/backend.log"
else
    print_error "Backend failed to start!"
    print_error "Check the logs: cat backend/backend.log"
    exit 1
fi

# Start Frontend
echo ""
echo "⚛️  Starting Frontend (React)..."
echo "-------------------------------"
cd "/Users/razashaikh/Desktop/final ro/frontend"

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    print_warning "node_modules not found. Installing dependencies..."
    npm install
fi

print_info "Starting frontend development server..."
# Start React in background
npm start > frontend.log 2>&1 &
FRONTEND_PID=$!

print_info "Frontend started with PID: $FRONTEND_PID"
print_info "Waiting for frontend to initialize..."

# Wait for frontend to start (React takes longer)
sleep 15

# Check if frontend is running
if curl -s http://localhost:3000/ > /dev/null; then
    print_status "Frontend is running successfully!"
else
    print_warning "Frontend may still be starting..."
fi

# Summary
echo ""
echo "🎉 FinVoice Application Status"
echo "=============================="
print_status "Backend (FastAPI): http://localhost:8000"
print_status "Frontend (React): http://localhost:3000"
print_status "API Documentation: http://localhost:8000/docs"
echo ""
echo "📋 Process Information:"
echo "   Backend PID: $BACKEND_PID"
echo "   Frontend PID: $FRONTEND_PID"
echo ""
echo "📊 Database Features Available:"
echo "   ✅ User Management (CRUD)"
echo "   ✅ Account Management"
echo "   ✅ Transaction Processing"
echo "   ✅ Financial Overview"
echo "   ✅ Portfolio Tracking"
echo "   ✅ Goal Management"
echo ""
echo "🛑 To stop both services:"
echo "   kill $BACKEND_PID $FRONTEND_PID"
echo ""
echo "📝 View logs:"
echo "   Backend: tail -f /Users/razashaikh/Desktop/final\\ ro/backend/backend.log"
echo "   Frontend: tail -f /Users/razashaikh/Desktop/final\\ ro/frontend/frontend.log"
echo ""
print_status "Full stack application is ready! 🚀"
