@echo off
REM GHL Onboarding System - Setup Script for Windows
REM This script automates the initial setup process

echo ========================================
echo GHL Healthcare Onboarding System Setup
echo ========================================
echo.

REM Check if .env exists
if not exist .env (
    echo [WARNING] .env file not found. Creating from .env.example...
    copy .env.example .env
    echo [SUCCESS] Created .env file
    echo.
    echo [WARNING] Please edit .env and add your API keys before continuing
    echo Required keys:
    echo - OPENAI_API_KEY
    echo - SUPABASE_URL
    echo - SUPABASE_ANON_KEY
    echo - SUPABASE_SERVICE_KEY
    echo - DATABASE_URL
    echo - JWT_SECRET
    echo.
    pause
)

REM Check Python
echo [INFO] Checking Python version...
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed
    exit /b 1
)
echo [SUCCESS] Python is installed

REM Check Node.js
echo [INFO] Checking Node.js version...
node --version > nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js is not installed
    exit /b 1
)
echo [SUCCESS] Node.js is installed

REM Setup Backend
echo.
echo [INFO] Setting up Backend...
cd backend

if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing Python dependencies...
pip install -q -r requirements.txt

echo [SUCCESS] Backend setup complete
cd ..

REM Setup Frontend
echo.
echo [INFO] Setting up Frontend...
cd frontend

if not exist .env.local (
    echo Creating .env.local from .env.example...
    copy ..\env.example .env.local
    echo [WARNING] Please update frontend\.env.local with your Supabase credentials
)

echo Installing Node.js dependencies...
call npm install

echo [SUCCESS] Frontend setup complete
cd ..

REM Summary
echo.
echo ========================================
echo [SUCCESS] Setup Complete!
echo ========================================
echo.
echo Next steps:
echo.
echo 1. Setup Supabase database:
echo    - Go to https://supabase.com
echo    - Create a new project
echo    - Run the migration from database\migrations\001_initial_schema.sql
echo.
echo 2. Start the backend:
echo    cd backend
echo    venv\Scripts\activate.bat
echo    uvicorn app.main:app --reload
echo.
echo 3. Start the frontend (in a new terminal):
echo    cd frontend
echo    npm run dev
echo.
echo 4. Access the application:
echo    - Backend API: http://localhost:8000
echo    - API Docs: http://localhost:8000/docs
echo    - Frontend: http://localhost:3000
echo.
echo For more details, see QUICKSTART.md
echo.
pause
