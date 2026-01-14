# install.ps1 - Cross-platform installation for SysMon
param(
    [switch]$AddToPath
)

Write-Host "=== SysMon Installation ===" -ForegroundColor Cyan
Write-Host ""

# Check Python version
$pythonVersion = python --version 2>&1
Write-Host "Python version: $pythonVersion" -ForegroundColor Green

# Install dependencies
Write-Host "`nInstalling dependencies..." -ForegroundColor Cyan
pip install -r requirements.txt

if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to install dependencies!" -ForegroundColor Red
    exit 1
}

# Install package in development mode
Write-Host "`nInstalling SysMon package..." -ForegroundColor Cyan
pip install -e .

if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to install SysMon!" -ForegroundColor Red
    exit 1
}

Write-Host "`n✓ SysMon installed successfully!" -ForegroundColor Green

# Instructions
Write-Host "`n=== How to use SysMon ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "Option 1: Use the launcher script (Recommended)" -ForegroundColor Yellow
Write-Host "  .\sysmon.bat monitor                    (Windows)" -ForegroundColor White
Write-Host "  python run.py monitor                   (All platforms)" -ForegroundColor White
Write-Host ""

Write-Host "Option 2: Use Python module directly" -ForegroundColor Yellow
Write-Host "  python -m sysmon.cli monitor" -ForegroundColor White
Write-Host ""

Write-Host "Option 3: Add to PATH for direct 'sysmon' command" -ForegroundColor Yellow

if ($AddToPath) {
    $currentPath = (Get-Location).Path
    $envPath = [Environment]::GetEnvironmentVariable("Path", "User")
    
    if ($envPath -notlike "*$currentPath*") {
        Write-Host "  Adding $currentPath to PATH..." -ForegroundColor Cyan
        $newPath = $envPath + ";" + $currentPath
        [Environment]::SetEnvironmentVariable("Path", $newPath, "User")
        Write-Host "  ✓ Added to PATH!" -ForegroundColor Green
        Write-Host "  Restart your terminal and use: sysmon monitor" -ForegroundColor White
    } else {
        Write-Host "  Already in PATH!" -ForegroundColor Green
    }
} else {
    Write-Host "  Run: .\install.ps1 -AddToPath" -ForegroundColor White
}

Write-Host "`n=== Quick Start ===" -ForegroundColor Cyan
Write-Host "  python run.py monitor              # Start the dashboard" -ForegroundColor White
Write-Host "  python run.py snapshot             # Take a snapshot" -ForegroundColor White
Write-Host "  python run.py config show          # View configuration" -ForegroundColor White
Write-Host "  python run.py --help               # See all commands" -ForegroundColor White
Write-Host ""