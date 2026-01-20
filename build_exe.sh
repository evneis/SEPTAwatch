#!/bin/bash
# Build script for creating Linux executable

echo "Building SEPTAwatch executable for Linux..."

# Install PyInstaller if not already installed
pip install pyinstaller

# Build the executable
pyinstaller --name=SEPTAwatch \
    --onefile \
    --noconsole \
    --icon="philadelphia-septa-metro-logo.png" \
    --add-data "requirements.txt:." \
    main.py

echo ""
echo "Build complete! Executable is in the 'dist' folder."
echo "You can find it at: dist/SEPTAwatch"
echo ""
echo "To run it: ./dist/SEPTAwatch"
