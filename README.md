# Simple Calendar App (Tkinter)

A lightweight desktop calendar for Windows (Python 3 + Tkinter).

## Features

* View any month in a selected year.
* Click a day to assign an item from a drop-down list (Meeting, Appointment, etc.).
* Days with an item are automatically highlighted.
* No external Python dependencies – relies only on the standard library.

## Running from source

```powershell
python calendar_app.py
```

## Packaging into a single EXE

Install PyInstaller if you don’t already have it:

```powershell
pip install pyinstaller
```

Then run:

```powershell
pyinstaller --onefile --noconsole calendar_app.py
```

You’ll find the standalone `calendar_app.exe` in the `dist/` directory.

## Tested on

* Windows 10 / Python 3.11 (official installer) – Tkinter is included by default.
