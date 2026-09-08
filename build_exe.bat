@echo off
setlocal EnableExtensions
cd /d "%~dp0"

echo Building SEPTAwatch executable...

pip install pyinstaller || goto :error
pyinstaller --noconfirm --clean SEPTAwatch.spec || goto :error

echo.
echo Build complete! Executable is in the 'dist' folder.
echo You can find it at: dist\SEPTAwatch.exe
pause
exit /b 0

:error
echo.
echo Build failed.
pause
exit /b 1
