#!/bin/bash

# Simple test script for running database tests against running server
echo "🧪 Testing FinVoice Database API"
echo "Server should be running on http://localhost:8000"
echo ""

cd "/Users/razashaikh/Desktop/final ro/backend"

# Check if server is running first
if curl -s http://localhost:8000/ > /dev/null; then
    echo "✅ Server is running, starting tests..."
    echo "================================"
    python test_database.py
    echo "================================"
    echo "Tests completed!"
else
    echo "❌ Server is not running!"
    echo "Please start the server first:"
    echo "  cd backend/app && python basic_main.py"
    exit 1
fi
