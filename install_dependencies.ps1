# Aether-Link Dependency Installation Script
# PowerShell script to install all required libraries

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Aether-Link Dependency Installer" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check Python version
Write-Host "[1/6] Checking Python version..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
Write-Host "Found: $pythonVersion" -ForegroundColor Green

if ($pythonVersion -notmatch "Python 3\.12") {
    Write-Host "WARNING: Python 3.12.x recommended. Current: $pythonVersion" -ForegroundColor Red
}

# Upgrade pip
Write-Host ""
Write-Host "[2/6] Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip

# Install core dependencies
Write-Host ""
Write-Host "[3/6] Installing core dependencies..." -ForegroundColor Yellow
pip install pyorbbecsdk2==2.0.18
pip install opencv-python==4.8.1.78
pip install numpy==1.26.2
pip install mediapipe==0.10.14
pip install PyQt6==6.6.1
pip install pyautogui==0.9.54

# Install security dependencies
Write-Host ""
Write-Host "[4/6] Installing security dependencies (3D Biometric)..." -ForegroundColor Yellow
pip install fastdtw==0.3.4
pip install scipy==1.11.4

# Install optional dependencies
Write-Host ""
Write-Host "[5/6] Installing optional dependencies..." -ForegroundColor Yellow
pip install pygetwindow==0.0.9

# Verify installation
Write-Host ""
Write-Host "[6/6] Verifying installation..." -ForegroundColor Yellow
Write-Host ""
Write-Host "Installed packages:" -ForegroundColor Cyan
pip list | Select-String -Pattern "pyorbbecsdk2|opencv-python|numpy|mediapipe|PyQt6|pyautogui|fastdtw|scipy|pygetwindow"

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  Installation Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Connect your Orbbec Gemini 335 camera" -ForegroundColor White
Write-Host "2. Run: python main.py" -ForegroundColor White
Write-Host ""
