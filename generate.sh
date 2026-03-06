#!/usr/bin/env bash
# The Brindles - Generate intro/outro
cd "$(dirname "$0")"

if [ ! -d ".venv" ]; then
    echo "Setup not complete. Run ./setup.sh first."
    exit 1
fi

source .venv/bin/activate
python generate.py
echo ""
read -p "Press Enter to close..."
