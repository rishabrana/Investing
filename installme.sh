#!/bin/bash

# Investment Analysis Toolkit - Automated Installation Script
# This script installs all dependencies for both frontend and backend

set -e  # Exit on any error

echo "=================================="
echo "Investment Analysis Toolkit Setup"
echo "=================================="
echo ""

# Check prerequisites
echo "Checking prerequisites..."

# Check for Python 3
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed"
    echo "Please install Python 3.8 or higher and try again"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "✓ Found Python $PYTHON_VERSION"

# Check for Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Error: Node.js is not installed"
    echo "Please install Node.js 18+ and try again"
    exit 1
fi

NODE_VERSION=$(node --version)
echo "✓ Found Node.js $NODE_VERSION"

# Check for npm
if ! command -v npm &> /dev/null; then
    echo "❌ Error: npm is not installed"
    echo "Please install npm and try again"
    exit 1
fi

NPM_VERSION=$(npm --version)
echo "✓ Found npm $NPM_VERSION"

echo ""
echo "=================================="
echo "Installing Backend Dependencies"
echo "=================================="
echo ""

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv .venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment and install dependencies
echo "Installing Python packages..."
source .venv/bin/activate
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt

echo "✓ Backend dependencies installed"

echo ""
echo "=================================="
echo "Installing Frontend Dependencies"
echo "=================================="
echo ""

cd frontend
echo "Installing npm packages (this may take a few minutes)..."
npm install

echo "✓ Frontend dependencies installed"

cd ..

echo ""
echo "=================================="
echo "Creating Data Directories"
echo "=================================="
echo ""

# Create necessary directories
mkdir -p data/raw
mkdir -p data/metrics
mkdir -p data/watchlists
mkdir -p data/credentials

echo "✓ Data directories created"

echo ""
echo "=================================="
echo "Installation Complete!"
echo "=================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Add your API keys:"
echo "   source .venv/bin/activate"
echo "   python -m cli.api_keys_cli add polygon.io YOUR_API_KEY"
echo ""
echo "2. Start the backend server:"
echo "   PYTHONPATH=\$(pwd) python3 -m uvicorn backend.api.main:app --reload --host 0.0.0.0 --port 8000"
echo ""
echo "3. In a new terminal, start the frontend:"
echo "   cd frontend && npm run dev"
echo ""
echo "4. Open your browser to:"
echo "   http://localhost:5173"
echo ""
echo "For more information, see README.md"
echo ""
