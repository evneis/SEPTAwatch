# SEPTAwatch

A PyQt6 application for monitoring SEPTA transit information.

## Installation

1. Install Python 3.7 or higher
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

```bash
python main.py
```

## Building Executables

### Windows

#### Quick Build (Using Scripts)

**Option 1: Using Batch File**
```bash
build_exe.bat
```

**Option 2: Using PowerShell**
```powershell
.\build_exe.ps1
```

#### Manual Build

1. Install PyInstaller:
   ```bash
   pip install pyinstaller
   ```

2. Build the executable:
   ```bash
   pyinstaller --name=SEPTAwatch --onefile --windowed --icon="philadelphia-septa-metro-logo.ico" main.py
   ```

3. Find your executable in the `dist` folder: `dist\SEPTAwatch.exe`

### Linux

#### Quick Build (Using Script)

1. Make the script executable:
   ```bash
   chmod +x build_exe.sh
   ```

2. Run the build script:
   ```bash
   ./build_exe.sh
   ```

#### Manual Build

1. Install PyInstaller:
   ```bash
   pip install pyinstaller
   ```

2. Build the executable:
   ```bash
   pyinstaller --name=SEPTAwatch --onefile --noconsole --icon="philadelphia-septa-metro-logo.png" main.py
   ```

3. Find your executable in the `dist` folder: `dist/SEPTAwatch`

4. Make it executable (if needed):
   ```bash
   chmod +x dist/SEPTAwatch
   ```

### Build Options Explained

- `--onefile`: Creates a single executable file (instead of a folder)
- `--windowed` (Windows) / `--noconsole` (Linux): Hides the console window (GUI app only)
- `--name=SEPTAwatch`: Sets the name of the executable
- `--icon=path/to/icon`: Add a custom icon (.ico for Windows, .png for Linux)

### Advanced: Using Spec File

For more control, you can use the generated spec file:
```bash
pyinstaller SEPTAwatch.spec
```

## Project Structure

```
SEPTAwatch/
├── main.py                              # Main application file
├── requirements.txt                     # Python dependencies
├── build_exe.bat                        # Windows batch build script
├── build_exe.ps1                        # PowerShell build script
├── build_exe.sh                         # Linux shell build script
├── philadelphia-septa-metro-logo.ico    # Windows icon
├── philadelphia-septa-metro-logo.png    # Linux icon
└── README.md                            # This file
```
