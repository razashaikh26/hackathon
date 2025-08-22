#!/bin/bash

# FinVoice Backend Startup and Test Script
# This script starts the server in background and runs tests

echo "🚀 Starting FinVoice Backend..."

# Kill any existing server on port 8000
echo "Checking for existing server on port 8000..."
if lsof -ti:8000 > /dev/null 2>&1; then
    echo "Killing existing server..."
    lsof -ti:8000 | xargs kill -9
    sleep 2
fi

# Start the server in background
echo "Starting server in background..."
cd "/Users/razashaikh/Desktop/final ro/backend/app"
nohup /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 basic_main.py > ../server.log 2>&1 &
SERVER_PID=$!

echo "Server started with PID: $SERVER_PID"
echo "Waiting for server to initialize..."

# Wait for server to start
sleep 8

# Check if server is running
if curl -s http://localhost:8000/ > /dev/null; then
    echo "✅ Server is running successfully!"
    echo "📋 Server logs are in: ../server.log"
    echo "🌐 API Documentation: http://localhost:8000/docs"
    echo ""
    echo "Now running database tests..."
    echo "================================"
    
    # Run the database tests
    cd "/Users/razashaikh/Desktop/final ro/backend"
    /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 test_database.py
    
    echo "================================"
    echo "Tests completed!"
    echo ""
    echo "Server is still running in background (PID: $SERVER_PID)"
    echo "To stop the server, run: kill $SERVER_PID"
    echo "To view logs: tail -f backend/server.log"
else
    echo "❌ Server failed to start!"
    echo "Check the logs: cat backend/server.log"
    exit 1
fi
