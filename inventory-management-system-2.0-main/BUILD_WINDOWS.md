# Windows Build Guide

This guide explains how to package the project for Windows as a standalone app.

## 1) Build the .exe (PyInstaller)

Install PyInstaller:

```bash
pip install pyinstaller
```

Build the GUI app:

```bash
python -m PyInstaller --onedir --windowed --name InventoryApp --paths src run_gui.py
```

Output:
- `dist/InventoryApp/InventoryApp.exe`

Notes:
- `--onedir` is recommended so the app can write data safely.
- Build artifacts (`dist/`, `build/`, `*.spec`) are ignored by git.

## 2) Create a Windows Installer (Inno Setup)

1. Install Inno Setup from the official site.
2. Use the script in `installer/InventoryApp.iss`.
3. Build the installer:

```bash
iscc installer\InventoryApp.iss
```

Output:
- `installer/Output/InventoryAppSetup.exe`

## Optional: Add an icon

If you have `icon.ico`, build with:

```bash
python -m PyInstaller --onedir --windowed --name InventoryApp --paths src --icon icon.ico run_gui.py
```

## Data Storage Location (Packaged App)

Packaged builds store data in:
- `%LOCALAPPDATA%\\InventoryApp\\`
