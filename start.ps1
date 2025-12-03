# Discord Bot Startup Script
# This script starts the Discord bot with the virtual environment

Write-Host "Starting Discord Bot..." -ForegroundColor Cyan

# Check if virtual environment exists
if (-not (Test-Path ".venv\Scripts\Activate.ps1")) {
    Write-Host "Virtual environment not found. Creating..." -ForegroundColor Yellow
    python -m venv .venv
    .\.venv\Scripts\python.exe -m pip install --upgrade pip
    Write-Host "Installing dependencies..." -ForegroundColor Yellow
    .\.venv\Scripts\pip.exe install -r requirements.txt
}

# Activate virtual environment and start bot
Write-Host "Activating virtual environment..." -ForegroundColor Green
& .\.venv\Scripts\python.exe bot.py

# Keep window open if there's an error
if ($LASTEXITCODE -ne 0) {
    Write-Host "`nBot stopped with errors. Press any key to exit..." -ForegroundColor Red
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}
