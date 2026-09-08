#!/bin/bash
# Build script for creating Linux executable
set -euo pipefail
cd "$(dirname "$0")"

echo "Building SEPTAwatch executable for Linux..."

pip install pyinstaller
pyinstaller --noconfirm --clean SEPTAwatch.spec

echo ""
echo "Build complete! Executable is in the 'dist' folder."
echo "You can find it at: dist/SEPTAwatch"
echo ""
echo "To run it: ./dist/SEPTAwatch"
