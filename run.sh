#!/bin/bash

echo "Starting FastAPI Application..."
echo ""

# Check if venv exists, if not create it
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate venv
source .venv/bin/activate

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -q -r requirements.txt

# Start the server
echo ""
echo "========================================"
echo "FastAPI Server is starting..."
echo "========================================"
echo ""
echo "Dashboard URL: http://localhost:8000/dashboard"
echo "API Docs: http://localhost:8000/docs"
echo ""

python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
