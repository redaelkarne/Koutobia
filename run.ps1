# PowerShell script to run FastAPI application on Windows

Write-Host "Starting FastAPI Application..." -ForegroundColor Cyan
Write-Host ""

# Check if venv exists, if not create it
if (-not (Test-Path ".venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv .venv
    Write-Host "Virtual environment created!" -ForegroundColor Green
}

# Activate venv
.\\.venv\Scripts\Activate.ps1

# Install dependencies
Write-Host ""
Write-Host "Installing dependencies..." -ForegroundColor Yellow
pip install -q -r requirements.txt
Write-Host "Dependencies installed!" -ForegroundColor Green

# Start the server
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "FastAPI Server is starting..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Dashboard URL: http://localhost:8000/dashboard" -ForegroundColor Green
Write-Host "API Docs: http://localhost:8000/docs" -ForegroundColor Green
Write-Host ""

python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

Read-Host "Press Enter to exit"
