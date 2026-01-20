# PowerShell build script for creating Windows executable
Write-Host "Building SEPTAwatch executable..." -ForegroundColor Green

# Install PyInstaller if not already installed
pip install pyinstaller

# Build the executable
pyinstaller --name=SEPTAwatch `
    --onefile `
    --windowed `
    --icon="$PSScriptRoot\philadelphia-septa-metro-logo.ico" `
    --add-data "requirements.txt;." `
    main.py

Write-Host "`nBuild complete! Executable is in the 'dist' folder." -ForegroundColor Green
Write-Host "You can find it at: dist\SEPTAwatch.exe" -ForegroundColor Cyan
