# Inventory Management System

I built this project to solve a simple, real problem: keep stock, sales, and invoices
organized without needing a big ERP. It is a Windows-first desktop app with a clean GUI
and a lightweight CLI for quick operations.

## What This App Does

- Manage products, categories, units, price, and quantity
- Track sales and generate PDF invoices
- Show sales history and audit logs
- Alert for low stock items
- Backup and restore the database
- Simple role-based login (Admin, Manager, Cashier)

## Interfaces

- GUI (Tkinter): the main workflow
- CLI: basic admin and sales flow

## Features

- Add, update, delete products
- Low stock alerts and inventory insights
- Sales entry with invoice PDF generation
- Sales history view
- Audit log for important actions
- Backup and restore
- Quick "Open Invoice Folder" action
- Keyboard shortcuts for faster work (Enter, Esc, Ctrl+S, Ctrl+N)

## Getting Started (End Users)

If you are a customer, install the app using:

```
installer\Output\InventoryAppSetup.exe
```

This is the only file you need to run. It creates the proper shortcuts and keeps all
app files in the correct location.

## Data Storage

Developer run:

- `data/inventory.db`
- `invoices/`
- `backups/`

Packaged Windows app:

- `%LOCALAPPDATA%\InventoryApp\`

## First Run

On first run, the app asks you to create the admin account. There is no default password.

## Run From Source (Developers)

Install dependency:

```bash
pip install reportlab
```

Run GUI:

```bash
python run_gui.py
```

Run CLI:

```bash
python run_cli.py
```

## Build Windows App

See `BUILD_WINDOWS.md` for the exact steps (PyInstaller + Inno Setup).

## Troubleshooting

- Invoice not showing:
  Use the "Open Invoice Folder" button. Packaged app saves to `%LOCALAPPDATA%\InventoryApp\invoices\`.
- Error: `python313.dll` not found:
  You ran only the EXE without `_internal`. Use the installer or full portable folder.
- Smart App Control block:
  Unsigned apps may be blocked. For selling, use code-signing.

## Author

Karan Shroff
