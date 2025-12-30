@echo off
echo ========================================
echo PLYMOUTH ROCK AUTOMATION SETUP
echo ========================================
echo.
echo This will install all required packages.
echo Installation will take 2-3 minutes.
echo.
echo Make sure Python is installed first!
echo.
pause

REM Use pushd to handle network paths
pushd "%~dp0"

echo.
echo Current directory: %CD%
echo.

echo [1/4] Checking Python installation...
python --version
if errorlevel 1 (
    echo.
    echo ERROR: Python not found!
    echo.
    echo Please install Python from https://www.python.org
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    popd
    exit /b
)

echo.
echo [2/4] Upgrading pip...
python -m pip install --upgrade pip

echo.
echo [3/4] Installing required packages from requirements.txt...
python -m pip install -r requirements.txt

echo.
echo [4/4] Installing Playwright browser...
python -m playwright install chromium

echo.
echo.
echo ========================================
echo INSTALLATION COMPLETE!
echo ========================================
echo.
echo Verification:
python -c "import streamlit; import pandas; import playwright; print('✓ All packages installed successfully!')"

echo.
echo.
echo NEXT STEPS:
echo 1. Make sure .env file exists with your credentials
echo 2. Close this window
echo 3. Double-click START.bat to run the automation
echo.
echo ========================================
pause

popd