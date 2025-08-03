@echo off
title Music Library Manager Launcher
color 0A

echo.
echo ========================================
echo    Music Library Manager Launcher
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from https://python.org
    echo.
    pause
    exit /b 1
)

REM Try the Windows-specific launcher first
if exist "launcher_windows.py" (
    echo [INFO] Using Windows-optimized launcher...
    python launcher_windows.py
) else (
    echo [INFO] Using standard launcher...
    python launcher.py
)

REM If there was an error, pause so user can see the message
if errorlevel 1 (
    echo.
    echo Press any key to exit...
    pause >nul
) 