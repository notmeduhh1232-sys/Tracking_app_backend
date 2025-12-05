# Quick start script for backend (without Docker)
# This script starts MongoDB, Redis, and the FastAPI backend

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  Backend Quick Start Script" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is installed
Write-Host "[1/5] Checking Python installation..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "❌ Python not found. Please install Python 3.11+" -ForegroundColor Red
    exit 1
}

# Check if we're in the backend directory
if (-not (Test-Path "main.py")) {
    Write-Host "❌ Please run this script from the backend/ directory" -ForegroundColor Red
    exit 1
}

# Install dependencies
Write-Host "`n[2/5] Installing Python dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to install dependencies" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Dependencies installed" -ForegroundColor Green

# Check MongoDB
Write-Host "`n[3/5] Checking MongoDB..." -ForegroundColor Yellow
Write-Host "⚠️  MongoDB must be running on localhost:27017" -ForegroundColor Yellow
Write-Host "   Option A: Use Docker: docker run -d -p 27017:27017 mongo:7.0" -ForegroundColor Gray
Write-Host "   Option B: Install locally from https://www.mongodb.com/try/download/community" -ForegroundColor Gray
Write-Host "   Option C: Use MongoDB Atlas (cloud)" -ForegroundColor Gray
$mongoResponse = Read-Host "`nIs MongoDB running? (y/n)"
if ($mongoResponse -ne "y") {
    Write-Host "Please start MongoDB first and try again." -ForegroundColor Red
    exit 1
}

# Check Redis
Write-Host "`n[4/5] Checking Redis..." -ForegroundColor Yellow
Write-Host "⚠️  Redis must be running on localhost:6379" -ForegroundColor Yellow
Write-Host "   Option A: Use Docker: docker run -d -p 6379:6379 redis:7.2-alpine" -ForegroundColor Gray
Write-Host "   Option B: Install locally from https://redis.io/download" -ForegroundColor Gray
Write-Host "   Note: Redis is optional but recommended for caching" -ForegroundColor Gray
$redisResponse = Read-Host "`nIs Redis running? (y/n)"
if ($redisResponse -ne "y") {
    Write-Host "⚠️  Continuing without Redis (caching disabled)" -ForegroundColor Yellow
}

# Start backend
Write-Host "`n[5/5] Starting FastAPI backend..." -ForegroundColor Yellow
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  Backend will be available at:" -ForegroundColor Green
Write-Host "  http://localhost:8000" -ForegroundColor Green
Write-Host "  API Docs: http://localhost:8000/docs" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Gray
Write-Host ""

python main.py
