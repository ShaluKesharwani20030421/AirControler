# Aether-Link Dependency Uninstallation Script
# PowerShell script to remove all project-specific libraries

Write-Host "========================================" -ForegroundColor Red
Write-Host "  Aether-Link Dependency Uninstaller" -ForegroundColor Red
Write-Host "========================================" -ForegroundColor Red
Write-Host ""
Write-Host "WARNING: This will remove all Aether-Link dependencies" -ForegroundColor Yellow
Write-Host ""

$confirmation = Read-Host "Continue? (y/N)"
if ($confirmation -ne 'y' -and $confirmation -ne 'Y') {
    Write-Host "Uninstall cancelled." -ForegroundColor Cyan
    exit
}

Write-Host ""
Write-Host "[1/3] Uninstalling core dependencies..." -ForegroundColor Yellow
pip uninstall -y pyorbbecsdk2
pip uninstall -y opencv-python
pip uninstall -y numpy
pip uninstall -y mediapipe
pip uninstall -y PyQt6
pip uninstall -y pyautogui

Write-Host ""
Write-Host "[2/3] Uninstalling security dependencies..." -ForegroundColor Yellow
pip uninstall -y fastdtw
pip uninstall -y scipy

Write-Host ""
Write-Host "[3/3] Uninstalling optional dependencies..." -ForegroundColor Yellow
pip uninstall -y pygetwindow

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  Uninstallation Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
