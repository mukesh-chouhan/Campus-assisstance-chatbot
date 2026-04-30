@echo off
title Campus Assistant Chatbot - Quick Start
color 0A

echo ========================================
echo   Campus Assistant Chatbot Setup
echo ========================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed!
    echo Please install Python 3.8 or higher from https://python.org
    pause
    exit /b 1
)

:: Check if Node.js is installed
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js is not installed!
    echo Please install Node.js from https://nodejs.org
    pause
    exit /b 1
)

echo [OK] Python and Node.js are installed
echo.

:: Ask user which setup to run
echo What would you like to do?
echo.
echo 1. Setup Backend (Python/Flask)
echo 2. Setup Frontend (React/Vite)
echo 3. Setup Both (Recommended for first time)
echo 4. Run Backend Server
echo 5. Run Frontend Server
echo 6. Run Both Servers
echo.
set /p choice="Enter choice (1-6): "

if "%choice%"=="1" goto setup_backend
if "%choice%"=="2" goto setup_frontend
if "%choice%"=="3" goto setup_both
if "%choice%"=="4" goto run_backend
if "%choice%"=="5" goto run_frontend
if "%choice%"=="6" goto run_both
goto invalid_choice

:setup_backend
echo.
echo ========================================
echo   Setting up Backend...
echo ========================================
cd backend
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)
call venv\Scripts\activate
echo Installing Python dependencies...
pip install -r requirements.txt
echo Initializing database...
python chatbot_engine.py
echo.
echo [SUCCESS] Backend setup complete!
echo.
pause
goto end

:setup_frontend
echo.
echo ========================================
echo   Setting up Frontend...
echo ========================================
cd CampusAssistancechatBot
echo Installing Node dependencies...
npm install
echo.
echo [SUCCESS] Frontend setup complete!
echo.
echo IMPORTANT: Make sure to create .env file with your API keys
echo.
pause
goto end

:setup_both
echo.
echo ========================================
echo   Setting up Backend...
echo ========================================
cd backend
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)
call venv\Scripts\activate
echo Installing Python dependencies...
pip install -r requirements.txt
echo Initializing database...
python chatbot_engine.py
cd ..
echo.
echo ========================================
echo   Setting up Frontend...
echo ========================================
cd CampusAssistancechatBot
echo Installing Node dependencies...
npm install
cd ..
echo.
echo [SUCCESS] Complete setup finished!
echo.
echo NEXT STEPS:
echo 1. Add your Google Gemini API key to CampusAssistancechatBot/.env
echo 2. Run option 6 to start both servers
echo.
pause
goto end

:run_backend
echo.
echo ========================================
echo   Starting Backend Server...
echo ========================================
cd backend
call venv\Scripts\activate
python app.py
goto end

:run_frontend
echo.
echo ========================================
echo   Starting Frontend Server...
echo ========================================
cd CampusAssistancechatBot
start cmd /k "npm run dev"
echo Frontend server starting in new window...
echo.
pause
goto end

:run_both
echo.
echo ========================================
echo   Starting Both Servers...
echo ========================================
echo.
echo Starting Backend Server...
cd backend
start cmd /k "call venv\Scripts\activate && python app.py"
timeout /t 3 /nobreak >nul
cd ..
echo Starting Frontend Server...
cd CampusAssistancechatBot
start cmd /k "npm run dev"
echo.
echo [SUCCESS] Both servers are starting!
echo.
echo Backend: http://localhost:5000
echo Frontend: http://localhost:5173
echo.
echo Press any key to return to menu...
pause >nul
goto end

:invalid_choice
echo.
echo [ERROR] Invalid choice! Please enter 1-6
echo.
pause
goto end

:end
echo.
echo Thank you for using Campus Assistant Chatbot!
echo.
