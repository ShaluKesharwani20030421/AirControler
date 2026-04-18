@echo off
echo.
echo ================================================================
echo   SIGNATURE RESET - Emergency Bypass
echo ================================================================
echo.
echo This will DELETE your saved signature.
echo The app will start UNLOCKED next time.
echo.
pause
echo.

if exist "signatures\my_signature.json" (
    del "signatures\my_signature.json"
    echo.
    echo [92m SUCCESS! Signature deleted.[0m
    echo.
    echo Next: Run [96mpython main.py[0m (will start UNLOCKED)
    echo.
) else (
    echo.
    echo [91m No signature file found.[0m
    echo The app is already UNLOCKED.
    echo.
)

echo ================================================================
echo.
pause
