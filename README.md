# SEPTAwatch

A PyQt6 application for monitoring SEPTA transit information using the public JSON APIs.

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

The app refreshes the active tab about every 30 seconds from `https://www3.septa.org/api/`:

- **Alerts** — `/Alerts/index.php`
- **Regional Rail** — `/TrainView/index.php`
- **Arrivals** — `/Arrivals/index.php` (station names must match [Regional Rail Inputs](https://www3.septa.org/VIRegionalRail.html))
- **Next to Arrive** — `/NextToArrive/index.php`
- **Bus / Trolley** — `/TransitView/index.php`
- **Metro** — `/v2/trips/` (not in the official Swagger; documented on [OpenDataPhilly](https://opendataphilly.org/datasets/septa-metro-apis/))
- **Elevators** — `/elevator/index.php`

Official Swagger (v1.0.2) lives at [app.septa.org](https://app.septa.org/). No API key is required.

## Tests

```bash
python -m unittest discover -s tests
```

Set `SEPTA_LIVE=1` to also hit the public API.

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
├── main.py                              # PyQt6 monitor UI
├── septa_api.py                         # SEPTA JSON API client
├── stations.py                          # Regional Rail station name map
├── tests/                               # Client tests against documented payloads
├── requirements.txt                     # Python dependencies
├── SEPTAwatch.spec                       # Shared PyInstaller spec
├── build_exe.bat                        # Windows batch build script
├── build_exe.ps1                        # PowerShell build script
├── build_exe.sh                         # Linux shell build script
├── philadelphia-septa-metro-logo.ico    # Windows icon
├── philadelphia-septa-metro-logo.png    # Linux / fallback icon
├── NEXT_STEPS.md                        # Suggested usability next steps
└── README.md                            # This file
```
