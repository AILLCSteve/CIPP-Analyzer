@echo off
title CIPP Spec Analyzer - Installer
color 0A

echo.
echo ==========================================
echo       CIPP Spec Analyzer - Installer
echo ==========================================
echo.
echo This will install the CIPP Spec Analyzer
echo.
pause

echo [1/3] Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found
    echo Please install Python from https://python.org
    pause
    exit /b 1
)
echo ✅ Python found

echo.
echo [2/3] Installing packages...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Package installation failed
    pause
    exit /b 1
)
echo ✅ Packages installed

echo.
echo [3/3] Creating launcher...
(
echo @echo off
echo title CIPP Spec Analyzer
echo echo Starting PDF service...
echo start /B python pdf_extractor.py
echo timeout /t 2 /nobreak ^>nul
echo echo Opening application...
echo powershell -Command "Invoke-Item 'cipp_analyzer_complete.html'"
echo echo.
echo echo Keep this window open while using the app
echo pause
) > "START_APP.bat"

echo ✅ Launcher created

echo.
echo ==========================================
echo          Installation Complete!
echo ==========================================
echo.
echo To use the app:
echo 1. Double-click "START_APP.bat"
echo 2. Configure your OpenAI API key
echo 3. Upload a PDF and analyze!
echo.
pause