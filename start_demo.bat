@echo off
REM ==============================================================================
REM NEUROTEACH AI — Single-Command Local Demo Launcher
REM Starts the FastAPI backend and Vite frontend simultaneously for local evaluation.
REM ==============================================================================

echo [1/3] Checking environment...
cd /d "%~dp0"

echo [2/3] Starting FastAPI Backend (Port 8000)...
start "NeuroTeach Backend" cmd /k "cd backend && venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

echo [3/3] Starting Vite Frontend (Port 5173)...
start "NeuroTeach Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo ==============================================================================
echo NEUROTEACH AI IS NOW LAUNCHING!
echo Backend API & Swagger: http://localhost:8000/docs
echo Backend Health & Provenance: http://localhost:8000/api/v1/health
echo Frontend Application: http://localhost:5173
echo ==============================================================================
echo.
pause

