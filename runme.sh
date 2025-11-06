#!/bin/bash

# Investment Analysis Toolkit - Run Script
# This script starts both backend and frontend servers

set -e  # Exit on any error

echo "=================================="
echo "Investment Analysis Toolkit"
echo "Starting Backend & Frontend Servers"
echo "=================================="
echo ""

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "❌ Error: Virtual environment not found"
    echo "Please run ./installme.sh first"
    exit 1
fi

# Check if node_modules exists
if [ ! -d "frontend/node_modules" ]; then
    echo "❌ Error: Frontend dependencies not installed"
    echo "Please run ./installme.sh first"
    exit 1
fi

# Get the project root directory
PROJECT_ROOT=$(pwd)

echo "Starting servers..."
echo ""

# Function to cleanup background processes on exit
cleanup() {
    echo ""
    echo "=================================="
    echo "Shutting down servers..."
    echo "=================================="

    # Kill all child processes
    jobs -p | xargs -r kill 2>/dev/null

    echo "Servers stopped."
    exit 0
}

# Set up trap to call cleanup on script exit
trap cleanup EXIT INT TERM

# Start backend server in background
echo "Starting Backend API server..."
echo "  → http://localhost:8000"
source .venv/bin/activate
PYTHONPATH=$PROJECT_ROOT python3 -m uvicorn backend.api.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Check if backend started successfully
if ! ps -p $BACKEND_PID > /dev/null; then
    echo "❌ Error: Backend server failed to start"
    exit 1
fi

echo "✓ Backend server running (PID: $BACKEND_PID)"
echo ""

# Start frontend server in background
echo "Starting Frontend dev server..."
echo "  → http://localhost:5173"
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

# Wait a moment for frontend to start
sleep 3

# Check if frontend started successfully
if ! ps -p $FRONTEND_PID > /dev/null; then
    echo "❌ Error: Frontend server failed to start"
    exit 1
fi

echo "✓ Frontend server running (PID: $FRONTEND_PID)"
echo ""

echo "=================================="
echo "✓ All servers running!"
echo "=================================="
echo ""
echo "Backend API:  http://localhost:8000"
echo "Frontend App: http://localhost:5173"
echo "API Docs:     http://localhost:8000/api/docs"
echo ""
echo "Press Ctrl+C to stop all servers"
echo "=================================="
echo ""

# Wait for both processes
wait
