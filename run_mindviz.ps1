# MindViz Quick Start Script
# Run this script to start both backend and frontend

Write-Host "=" * 60
Write-Host "🌱 MindViz - Starting Application" -ForegroundColor Green
Write-Host "=" * 60
Write-Host ""

# Get the script directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# Check if .env file exists
if (-not (Test-Path "$ScriptDir\backend\.env")) {
    Write-Host "⚠️  WARNING: backend\.env file not found!" -ForegroundColor Yellow
    Write-Host "   Create backend\.env with your GEMINI_API_KEY" -ForegroundColor Yellow
    Write-Host ""
}

# Start Backend in new window
Write-Host "🚀 Starting Backend Server..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$ScriptDir\backend'; python server.py"

# Wait for backend to start
Write-Host "⏳ Waiting for backend to initialize..." -ForegroundColor Gray
Start-Sleep -Seconds 3

# Start Frontend in new window
Write-Host "🚀 Starting Frontend Application..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$ScriptDir\frontend'; python main.py"

Write-Host ""
Write-Host "=" * 60
Write-Host "✅ MindViz is starting!" -ForegroundColor Green
Write-Host ""
Write-Host "📍 Backend: http://localhost:8000" -ForegroundColor White
Write-Host "📍 API Docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "Close this window when done, or close the app windows" -ForegroundColor Gray
Write-Host "=" * 60
