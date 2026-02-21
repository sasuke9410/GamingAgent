@echo off
echo ========================================
echo Pokemon Red - Quick Start
echo ========================================
echo.

REM Check if virtual environment exists
if not exist .venv\Scripts\activate.bat (
    echo ERROR: .venv not found
    echo Please run: python -m venv .venv
    pause
    exit /b 1
)

REM Activate virtual environment
call .venv\Scripts\activate.bat

REM Quick test run (5 steps)
echo Starting Pokemon Red test run (5 steps)...
echo.
powershell -File run_pokemon_red_test.ps1 -MaxSteps 5 -ObservationMode vision -TokenLimit 1500

pause