# ByteBouncer - Administrator Launch Script
# This script launches ByteBouncer with administrator privileges

Write-Host "🛡️ ByteBouncer Administrator Launch" -ForegroundColor Red
Write-Host "=================================" -ForegroundColor Red

# Check if already running as admin
$currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
$isAdmin = $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if ($isAdmin) {
    Write-Host "✅ Already running as Administrator" -ForegroundColor Green
} else {
    Write-Host "⚠️ Not running as Administrator - requesting elevation..." -ForegroundColor Yellow
    
    # Restart as administrator
    Start-Process PowerShell -Verb RunAs -ArgumentList "-ExecutionPolicy Bypass -File `"$PSCommandPath`""
    exit
}

Write-Host "🚀 Starting ByteBouncer with Administrator privileges..." -ForegroundColor Cyan

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& "venv\Scripts\Activate.ps1"

# Check if activation was successful
if ($env:VIRTUAL_ENV) {
    Write-Host "✅ Virtual environment activated: $env:VIRTUAL_ENV" -ForegroundColor Green
} else {
    Write-Host "❌ Failed to activate virtual environment" -ForegroundColor Red
    Write-Host "Press any key to exit..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit 1
}

# Run ByteBouncer
Write-Host "🎯 Launching ByteBouncer as Administrator..." -ForegroundColor Cyan
Write-Host "⚠️ CAUTION: You can now delete system files - be careful!" -ForegroundColor Yellow

python app.py

Write-Host "ByteBouncer closed." -ForegroundColor Gray
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")