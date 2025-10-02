# ByteBouncer - PowerShell Launch Script
# Activates virtual environment and runs ByteBouncer

Write-Host "🚀 Starting ByteBouncer..." -ForegroundColor Green
Write-Host "Activating virtual environment..." -ForegroundColor Yellow

# Activate virtual environment
& "venv\Scripts\Activate.ps1"

# Check if activation was successful
if ($env:VIRTUAL_ENV) {
    Write-Host "✅ Virtual environment activated: $env:VIRTUAL_ENV" -ForegroundColor Green
} else {
    Write-Host "❌ Failed to activate virtual environment" -ForegroundColor Red
    exit 1
}

# Run the application
Write-Host "🎯 Launching ByteBouncer..." -ForegroundColor Cyan
python app.py