# SEPTAwatch

A PyQt6 application for monitoring SEPTA transit information.

## Installation

1. Install Python 3.9 or higher
2. Create a virtual environment (recommended):
   ```bash
   python -m venv .venv
   source .venv/bin/activate   # Windows: .venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

```bash
python main.py
```

## Building Executables

The three platform scripts all run the same `SEPTAwatch.spec` file. From the project root:

### Windows

```bash
build_exe.bat
```

or:

```powershell
.\build_exe.ps1
```

The executable lands at `dist\SEPTAwatch.exe`.

### Linux

```bash
chmod +x build_exe.sh
./build_exe.sh
```

The executable lands at `dist/SEPTAwatch`. Make it executable if needed:

```bash
chmod +x dist/SEPTAwatch
```

### Manual build

```bash
pip install pyinstaller
pyinstaller --noconfirm --clean SEPTAwatch.spec
```

### Build options

The spec file currently:

- Produces a single-file GUI app (`console=False`)
- Names the binary `SEPTAwatch`
- Bundles the `.ico` and `.png` logos so the window icon works in frozen builds
- Uses `.ico` on Windows and `.png` elsewhere

To tweak those choices, edit `SEPTAwatch.spec` and rebuild.

## Project Structure

```
SEPTAwatch/
├── main.py                              # Main application file
├── requirements.txt                     # Python dependencies
├── SEPTAwatch.spec                     # Shared PyInstaller spec
├── build_exe.bat                        # Windows batch build script
├── build_exe.ps1                        # PowerShell build script
├── build_exe.sh                         # Linux shell build script
├── philadelphia-septa-metro-logo.ico    # Windows icon
├── philadelphia-septa-metro-logo.png    # Linux / fallback icon
├── NEXT_STEPS.md                       # Suggested usability next steps
└── README.md                            # This file
```
