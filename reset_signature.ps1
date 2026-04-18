# Reset Signature - Emergency Bypass
# Use this if you forgot your signature and are locked out

Write-Host ""
Write-Host "================================================================" -ForegroundColor Yellow
Write-Host "  SIGNATURE RESET UTILITY" -ForegroundColor Yellow
Write-Host "================================================================" -ForegroundColor Yellow
Write-Host ""

$sigFile = "signatures\my_signature.json"

if (Test-Path $sigFile) {
    Write-Host "Found signature file: $sigFile" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "This will DELETE your saved signature." -ForegroundColor Red
    Write-Host "The app will start UNLOCKED next time." -ForegroundColor Green
    Write-Host ""
    
    $confirm = Read-Host "Are you sure? (yes/no)"
    
    if ($confirm -eq "yes") {
        Remove-Item $sigFile
        Write-Host ""
        Write-Host "✅ Signature deleted!" -ForegroundColor Green
        Write-Host ""
        Write-Host "Next steps:" -ForegroundColor Cyan
        Write-Host "  1. Run: python main.py" -ForegroundColor White
        Write-Host "     (App will start UNLOCKED)" -ForegroundColor White
        Write-Host ""
        Write-Host "  2. Optional: Record new signature" -ForegroundColor White
        Write-Host "     python record_signature.py" -ForegroundColor White
        Write-Host ""
    } else {
        Write-Host ""
        Write-Host "❌ Cancelled. Signature NOT deleted." -ForegroundColor Yellow
        Write-Host ""
    }
} else {
    Write-Host "❌ No signature file found." -ForegroundColor Red
    Write-Host "   File: $sigFile" -ForegroundColor Gray
    Write-Host ""
    Write-Host "The app is already UNLOCKED." -ForegroundColor Green
    Write-Host ""
}

Write-Host "================================================================" -ForegroundColor Yellow
Write-Host ""
