@echo off
echo Starting FastAPI Application...
echo.

REM Check if venv exists, if not create it
if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
)

REM Activate venv
call .venv\Scripts\activate.bat

REM Install dependencies
echo.
echo Installing dependencies...
pip install -q -r requirements.txt

REM Start the server
echo.
echo ========================================
echo FastAPI Server is starting...
echo ========================================
echo.
echo Dashboard URL: http://localhost:8000/dashboard
echo API Docs: http://localhost:8000/docs
echo.

python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

pause
