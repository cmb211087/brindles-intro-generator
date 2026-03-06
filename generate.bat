@echo off
REM The Brindles - Generate intro/outro
cd /d "%~dp0"

if not exist ".venv" (
    echo Setup not complete. Run setup.bat first.
    pause
    exit /b 1
)

call .venv\Scripts\activate.bat
python generate.py
echo.
pause
