@echo off
echo ============================================
echo  ABPS - Automatic Block Planning System
echo  Railway Maintenance Scheduler
echo ============================================
echo.

cd /d "%~dp0"

echo [1/3] Initializing database with synthetic data...
python backend/init_db.py
if %errorlevel% neq 0 (
    echo ERROR: Database init failed. Make sure you've run: pip install -r requirements.txt
    pause
    exit /b 1
)

echo.
echo [2/3] Starting FastAPI backend on http://localhost:8000 ...
start "ABPS Backend" cmd /k "cd /d %~dp0 && uvicorn backend.main:app --reload --port 8000"

echo Waiting for backend to start...
timeout /t 4 /nobreak >nul

echo.
echo [3/3] Starting Streamlit dashboard on http://localhost:8501 ...
start "ABPS Dashboard" cmd /k "cd /d %~dp0 && streamlit run frontend/app.py --server.port 8501"

echo.
echo ============================================
echo  ABPS is running!
echo  Dashboard : http://localhost:8501
echo  API Docs  : http://localhost:8000/docs
echo.
echo  Login with:
echo    admin    / admin123
echo    planner1 / plan123
echo    approver / approve123
echo ============================================
echo.
pause
