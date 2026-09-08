# PowerShell build script for creating Windows executable
$ErrorActionPreference = "Stop"
Set-Location -Path $PSScriptRoot

Write-Host "Building SEPTAwatch executable..." -ForegroundColor Green

pip install pyinstaller
if ($LASTEXITCODE -ne 0) { throw "Failed to install PyInstaller" }

pyinstaller --noconfirm --clean SEPTAwatch.spec
if ($LASTEXITCODE -ne 0) { throw "PyInstaller build failed" }

Write-Host "`nBuild complete! Executable is in the 'dist' folder." -ForegroundColor Green
Write-Host "You can find it at: dist\SEPTAwatch.exe" -ForegroundColor Cyan
