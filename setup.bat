@echo off
setlocal enabledelayedexpansion
REM The Brindles - One-time setup script (Windows)

echo ==================================
echo   The Brindles - Setup
echo ==================================
echo.

cd /d "%~dp0"

REM Check for Python
set "PYTHON="
where py >nul 2>&1
if !ERRORLEVEL! equ 0 (
    set "PYTHON=py -3"
    goto :found_python
)
where python >nul 2>&1
if !ERRORLEVEL! equ 0 (
    set "PYTHON=python"
    goto :found_python
)
echo Python 3 not found.
echo Please install Python 3.10+ from https://python.org
echo Make sure to check "Add Python to PATH" during installation.
pause
exit /b 1

:found_python
REM Verify version
!PYTHON! -c "import sys; exit(0 if sys.version_info >= (3, 10) else 1)"
if !ERRORLEVEL! neq 0 (
    echo Python 3.10+ required.
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('!PYTHON! -c "import sys; print(str(sys.version_info.major) + '.' + str(sys.version_info.minor))"') do set "PY_VERSION=%%i"
echo Found Python !PY_VERSION!

REM Check for FFmpeg
where ffmpeg >nul 2>&1
if !ERRORLEVEL! neq 0 (
    echo FFmpeg not found.
    echo Please install FFmpeg from https://ffmpeg.org/download.html
    echo Or use: winget install Gyan.FFmpeg
    pause
    exit /b 1
)
echo Found FFmpeg

REM Create virtual environment
if not exist ".venv" (
    echo.
    echo Creating virtual environment...
    !PYTHON! -m venv .venv
)

echo Activating virtual environment...
call .venv\Scripts\activate.bat

REM Install dependencies
echo Installing Python dependencies...
pip install --upgrade pip -q
pip install -r requirements.txt -q

REM Download Montserrat-Bold font if not present
if not exist "assets\fonts\Montserrat-Bold.ttf" (
    echo.
    echo Downloading Montserrat-Bold font...
    if not exist "assets\fonts" mkdir "assets\fonts"
    curl -L -o "assets\fonts\Montserrat-Bold.ttf" "https://github.com/JulietaUla/Montserrat/raw/master/fonts/ttf/Montserrat-Bold.ttf" 2>nul
    if !ERRORLEVEL! neq 0 (
        echo Could not download font automatically.
        echo Please download Montserrat-Bold.ttf from Google Fonts
        echo and place it in assets\fonts\
    )
)

REM Create directories
if not exist "input" mkdir input
if not exist "output" mkdir output

echo.
echo ==================================
echo   Setup complete!
echo ==================================
echo.
echo Next steps:
echo   1. Add your logo as: assets\logo.png
echo   2. Add intro music as: assets\intro_music.mp3
echo   3. Add outro music as: assets\outro_music.mp3
echo   4. Drop raw clips into input\
echo   5. Double-click generate.bat
echo.
echo See README.md for details on finding free music.
echo.
endlocal
pause
