@echo off
setlocal

set "ROOT=%~dp0"
cd /d "%ROOT%backend"

if not exist "venv\Scripts\python.exe" (
    echo [SETUP] Creating virtual environment...
    python -m venv venv
)

call venv\Scripts\activate.bat

echo [SETUP] Installing dependencies...
pip install -r requirements.txt -q

echo [READY] Starting backend at http://localhost:8000
python -m uvicorn app.main:app --reload --port 8000

pause
