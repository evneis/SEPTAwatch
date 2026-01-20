@echo off
REM Build script for creating Windows executable
echo Building SEPTAwatch executable...

REM Install PyInstaller if not already installed
pip install pyinstaller

REM Build the executable
pyinstaller --name=SEPTAwatch ^
    --onefile ^
    --windowed ^
    --icon="C:\Projects\SEPTAwatch\philadelphia-septa-metro-logo.ico" ^
    --add-data "requirements.txt;." ^
    --hidden-import PyQt6 ^
    --hidden-import PyQt6.QtCore ^
    --hidden-import PyQt6.QtGui ^
    --hidden-import PyQt6.QtWidgets ^
    --collect-submodules PyQt6 ^
    --collect-all PyQt6 ^
    main.py

echo.
echo Build complete! Executable is in the 'dist' folder.
echo You can find it at: dist\SEPTAwatch.exe
pause
