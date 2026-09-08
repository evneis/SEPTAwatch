# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for SEPTAwatch. Shared by the Windows and Linux build scripts."""

import sys

icon = (
    "philadelphia-septa-metro-logo.ico"
    if sys.platform == "win32"
    else "philadelphia-septa-metro-logo.png"
)

a = Analysis(
    ["main.py"],
    pathex=[],
    binaries=[],
    datas=[
        ("philadelphia-septa-metro-logo.ico", "."),
        ("philadelphia-septa-metro-logo.png", "."),
    ],
    hiddenimports=[
        "PyQt6",
        "PyQt6.QtCore",
        "PyQt6.QtGui",
        "PyQt6.QtWidgets",
        "septa_api",
        "stations",
        "requests",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="SEPTAwatch",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon,
)
