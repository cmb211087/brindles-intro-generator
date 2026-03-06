#!/usr/bin/env bash
# The Brindles - One-time setup script (Mac/Linux)
set -e

echo "=================================="
echo "  The Brindles - Setup"
echo "=================================="
echo ""

cd "$(dirname "$0")"

# Check for Python 3.10+
if command -v python3 &>/dev/null; then
    PYTHON=python3
elif command -v python &>/dev/null; then
    PYTHON=python
else
    echo "Python 3 not found."
    if command -v brew &>/dev/null; then
        echo "Installing Python via Homebrew..."
        brew install python@3.12
        PYTHON=python3
    else
        echo "Please install Python 3.10+ from https://python.org"
        exit 1
    fi
fi

# Verify version
PY_VERSION=$($PYTHON -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
PY_MAJOR=$($PYTHON -c "import sys; print(sys.version_info.major)")
PY_MINOR=$($PYTHON -c "import sys; print(sys.version_info.minor)")

if [ "$PY_MAJOR" -lt 3 ] || ([ "$PY_MAJOR" -eq 3 ] && [ "$PY_MINOR" -lt 10 ]); then
    echo "Python 3.10+ required. Found Python $PY_VERSION"
    exit 1
fi
echo "Found Python $PY_VERSION"

# Check for FFmpeg
if ! command -v ffmpeg &>/dev/null; then
    echo "FFmpeg not found."
    if command -v brew &>/dev/null; then
        echo "Installing FFmpeg via Homebrew..."
        brew install ffmpeg
    else
        echo "Please install FFmpeg: https://ffmpeg.org/download.html"
        exit 1
    fi
else
    echo "Found FFmpeg"
fi

# Create virtual environment
if [ ! -d ".venv" ]; then
    echo ""
    echo "Creating virtual environment..."
    $PYTHON -m venv .venv
fi

echo "Activating virtual environment..."
source .venv/bin/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip -q
pip install -r requirements.txt -q

# Download Montserrat-Bold font if not present
FONT_DIR="assets/fonts"
FONT_FILE="$FONT_DIR/Montserrat-Bold.ttf"
if [ ! -f "$FONT_FILE" ]; then
    echo ""
    echo "Downloading Montserrat-Bold font..."
    mkdir -p "$FONT_DIR"
    curl -L -o "$FONT_FILE" \
        "https://github.com/JulietaUla/Montserrat/raw/master/fonts/ttf/Montserrat-Bold.ttf" \
        2>/dev/null || {
        echo "Could not download font automatically."
        echo "Please download Montserrat-Bold.ttf from Google Fonts and place it in $FONT_DIR/"
    }
fi

# Create directories
mkdir -p input output

echo ""
echo "=================================="
echo "  Setup complete!"
echo "=================================="
echo ""
echo "Next steps:"
echo "  1. Add your logo as: assets/logo.png"
echo "  2. Add intro music as: assets/intro_music.mp3"
echo "  3. Add outro music as: assets/outro_music.mp3"
echo "  4. Drop raw clips into input/"
echo "  5. Run: ./generate.sh"
echo ""
echo "See README.md for details on finding free music."
