#!/bin/bash
# Deployment script for Dirac Wallet Backend

# Exit on any error
set -e

echo "Starting deployment of Dirac Wallet API..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is required but not installed. Please install Python 3."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "pip3 is required but not installed. Please install pip3."
    exit 1
fi

# Set up virtual environment
echo "Setting up virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Run tests
echo "Running tests..."
# Add test command here
# python -m pytest tests/

# Set up environment variables
echo "Setting up environment variables..."
export BACKEND_PORT=8000
export BACKEND_HOST="0.0.0.0"
export LOG_LEVEL="info"

# Start Uvicorn server with Gunicorn
echo "Starting server..."
if [ "$1" == "prod" ]; then
    # Production mode with Gunicorn
    echo "Starting in production mode..."
    pip install gunicorn uvloop httptools
    gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker -b $BACKEND_HOST:$BACKEND_PORT --daemon
    echo "Server started in background (production mode)"
else
    # Development mode
    echo "Starting in development mode..."
    uvicorn main:app --host $BACKEND_HOST --port $BACKEND_PORT --reload
fi

echo "Deployment complete!" 