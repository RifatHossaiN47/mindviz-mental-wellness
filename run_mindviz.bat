@echo off
title MindViz Launcher

echo ============================================================
echo 🌱 MindViz - Starting Application
echo ============================================================
echo.

REM Get the directory where this script is located
set "SCRIPT_DIR=%~dp0"

REM Check if .env file exists
if not exist "%SCRIPT_DIR%backend\.env" (
    echo WARNING: backend\.env file not found!
    echo Create backend\.env with your GEMINI_API_KEY
    echo.
)

echo Starting Backend Server...
start "MindViz Backend" cmd /k "cd /d "%SCRIPT_DIR%backend" && python server.py"

echo Waiting for backend to initialize...
timeout /t 3 /nobreak > nul

echo Starting Frontend Application...
start "MindViz Frontend" cmd /k "cd /d "%SCRIPT_DIR%frontend" && python main.py"

echo.
echo ============================================================
echo MindViz is starting!
echo.
echo Backend: http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo.
echo Close this window or press any key to exit launcher
echo ============================================================
pause > nul
