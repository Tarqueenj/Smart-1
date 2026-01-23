@echo off
echo 🚀 SmartTriage AI - Quick Setup Script
echo =====================================

echo.
echo 1. Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found. Please install Python 3.8+ first.
    pause
    exit /b 1
)
echo ✅ Python found

echo.
echo 2. Creating virtual environment...
if not exist "venv" (
    python -m venv venv
    echo ✅ Virtual environment created
) else (
    echo ✅ Virtual environment already exists
)

echo.
echo 3. Activating virtual environment...
call venv\Scripts\activate
echo ✅ Virtual environment activated

echo.
echo 4. Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Failed to install dependencies
    pause
    exit /b 1
)
echo ✅ Dependencies installed

echo.
echo 5. Setting up environment file...
if not exist ".env" (
    copy .env.example .env
    echo ✅ Environment file created
    echo ⚠️  Please edit .env file with your API keys
) else (
    echo ✅ Environment file already exists
)

echo.
echo 6. Starting the application...
echo 🌐 Application will be available at: http://localhost:5000
echo 🔐 Login credentials:
echo    Nurse: nurse / nurse123
echo    Clinician: clinician / clinician123
echo    Admin: admin / admin123
echo.
echo Press Ctrl+C to stop the server
echo.

python app.py

pause
