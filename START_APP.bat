@echo off
echo ========================================
echo Plymouth Rock Quote Automation
echo ========================================
echo.

REM Use pushd to handle UNC paths (network drives)
pushd "%~dp0"

REM Verify .env file exists
if not exist ".env" (
    echo ERROR: .env file not found!
    echo.
    echo Make sure .env file exists in this folder with:
    echo PR_USERNAME=your_username
    echo PR_PASSWORD=your_password
    echo.
    pause
    popd
    exit /b
)

echo Current directory: %CD%
echo .env file found!
echo.
echo Starting automation interface...
echo A browser window will open automatically.
echo.
echo To stop: Close the browser tab or use Reset App
echo.
echo ========================================
echo.

REM Start Streamlit using python -m (works without PATH)
python -m streamlit run app.py --server.maxUploadSize 200

if errorlevel 1 (
    echo.
    echo ERROR: Failed to start Streamlit
    echo.
    echo Solutions:
    echo 1. Run INSTALL.bat again
    echo 2. Close this window and restart your computer
    echo 3. Contact Swetha for help
    echo.
)

REM Clean up the mapped drive
popd

pause