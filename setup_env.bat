@echo off
echo ====================================
echo Aether-Link Environment Setup
echo ====================================
echo.

if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
    echo Virtual environment created.
    echo.
) else (
    echo Virtual environment already exists.
    echo.
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Installing dependencies...
pip install --upgrade pip
pip install -r requirements.txt

echo.
echo ====================================
echo Setup complete!
echo ====================================
echo.
echo To run Aether-Link:
echo   1. Activate the environment: venv\Scripts\activate
echo   2. Run the application: python main.py
echo.
pause
