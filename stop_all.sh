#!/bin/bash

# FinVoice Full Stack Stop Script
# Stops both backend and frontend servers

echo "🛑 Stopping FinVoice Full Stack Application..."

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Stop backend (port 8000)
if lsof -ti:8000 > /dev/null 2>&1; then
    print_warning "Stopping backend server (port 8000)..."
    lsof -ti:8000 | xargs kill -9
    print_status "Backend stopped"
else
    echo "Backend not running"
fi

# Stop frontend (port 3000)
if lsof -ti:3000 > /dev/null 2>&1; then
    print_warning "Stopping frontend server (port 3000)..."
    lsof -ti:3000 | xargs kill -9
    print_status "Frontend stopped"
else
    echo "Frontend not running"
fi

# Clean up any remaining node/python processes
pkill -f "react-scripts start" 2>/dev/null || true
pkill -f "basic_main.py" 2>/dev/null || true

print_status "All FinVoice services stopped!"
