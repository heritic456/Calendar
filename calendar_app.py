#!/usr/bin/env python3
"""Simple desktop calendar app for Windows (Python + Tkinter).

Features
--------
1. Displays a monthly calendar for a selectable year.
2. Click on any day to assign an event from a drop-down list.
3. Highlights days that have an assigned event.

This script uses only Python standard-library modules, so there is no
extra runtime dependency beyond a normal Python 3 installation that
includes Tk (which the official Windows installer does).

Packaging
~~~~~~~~~
After testing, you can create a standalone executable with::

    pyinstaller --onefile --noconsole calendar_app.py

(see README.md for details).
"""
from __future__ import annotations

import calendar
import datetime as _dt
import sys
import tkinter as tk
from tkinter import ttk, font as tkfont, messagebox
from typing import Dict, Tuple
from pathlib import Path
import json

# Predefined list of items that can be added to a day.
EVENT_CHOICES = [
    "Butter Pecan",
    "Andes Mint Avalanche",
    "Dark Chocolate Decadence",
    "Caramel Fudge Cookie Dough",
    "Oreo Cookie Overload",
    "Georgia Peach",
    "Caramel Cashew",
    "Really Reese's",
    "Caramel Chocolate Pecan",
    "Chocolate Covered Strawberry",
    "Mint Cookie",
    "Chocolate Heath Crunch"
    "Double Strawberry",
    "Chocolate Caramel Twist",
    "Devil's Food Cake",
    "Caramel Peanut Buttercup",
    "Chocolate Volcano",
    "Caramel Pecan"
    "Crazy for Cookie Dough",
    "Snickers Swirl",
    "Saled Double Caramel Pecan",
    "Dark Chocolate Decadence",
    "Mint Explosion",
    "Turtle",
    "Dark Chocolate PB Crunch",
    "Oreo Cookie Cheesecake",
    "Caramel Turtle",
    "Double Strawberry",
    "Turtle Cheesecake",
    "Georgia Peach"
]

# Type alias for dictionary key: (year, month, day)
DateKey = Tuple[int, int, int]
# Stored data per date: {'choice': str, 'note': str}
DateData = Dict[str, str]


class CalendarApp:
    """Main GUI application."""

    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("")
        # Set initial window size
        self.root.geometry("900x700")
        # Larger font for day buttons
        self.day_font = tkfont.Font(size=12)
        self.week_font = tkfont.Font(size=16, weight="bold")
        # Allow the window to be resized by the user.
        self.root.resizable(True, True)

        # Set global background color
        self.root.configure(bg="#e8f4ff", highlightthickness=0, bd=0)
        style = ttk.Style(self.root)
        style.configure("Calendar.TFrame", background="#e8f4ff")
        style.configure("Calendar.TLabel", background="#e8f4ff")

        # Storage for events -> mapping of (y, m, d) to data dict
        self.events: Dict[DateKey, DateData] = {}

        # Load any previously saved events
        self._data_file = Path(__file__).with_name("events.json")
        self._load_events()

        # Title label
        tk.Label(self.root, text="Flavor of the Day/Speciality Calendar", font=("Helvetica", 20, "bold"), bg="#e8f4ff", fg="black", bd=0, highlightthickness=0).grid(row=0, column=0, pady=(10,5))

        # --- Header (year & month selectors) -------------------------------
        header = tk.Frame(self.root, bg="#e8f4ff", padx=10, pady=10, highlightthickness=0, bd=0)
        header.grid(row=1, column=0, sticky="EW")

        current_year = _dt.date.today().year
        years = [str(y) for y in range(current_year - 5, current_year + 6)]
        months = list(calendar.month_name)[1:]  # Skip empty string at index 0

        self.year_var = tk.StringVar(value=str(current_year))
        self.month_var = tk.StringVar(value=months[_dt.date.today().month - 1])

        year_box = ttk.Combobox(
            header,
            textvariable=self.year_var,
            values=years,
            width=5,
            state="readonly",
        )
        month_box = ttk.Combobox(
            header,
            textvariable=self.month_var,
            values=months,
            width=10,
            state="readonly",
        )
        month_box.bind("<<ComboboxSelected>>", lambda e: self.draw_calendar())
        year_box.bind("<<ComboboxSelected>>", lambda e: self.draw_calendar())

        month_box.grid(row=0, column=0, padx=(0, 5))
        year_box.grid(row=0, column=1)

        # Clear month button
        ttk.Button(header, text="Clear Month", command=self.clear_month).grid(row=0, column=2, padx=(10,0))

        # --- Calendar grid container --------------------------------------
        self.grid_frame = tk.Frame(self.root, bg="#e8f4ff", padx=10, pady=10, highlightthickness=0, bd=0)
        self.grid_frame.grid(row=2, column=0, sticky="NSEW")

        # Allow calendar grid to grow with window size
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(2, weight=1)

        # Weekday headers
        for i, dayname in enumerate(calendar.day_abbr):
            tk.Label(self.grid_frame, text=dayname, bg="#e8f4ff", fg="black", font=self.week_font, bd=0).grid(row=0, column=i, padx=3, pady=3, sticky="NSEW")
            self.grid_frame.columnconfigure(i, weight=1)

        self.day_btns: Dict[Tuple[int, int], tk.Button] = {}
        self.draw_calendar()

    # ---------------------------------------------------------------------
    # UI helpers
    # ---------------------------------------------------------------------
    def draw_calendar(self) -> None:
        """Draw (or redraw) the calendar for the selected month/year."""
        # Clear existing day buttons (row >= 1)
        for child in self.grid_frame.winfo_children():
            info = child.grid_info()
            if info.get("row", 0) > 0:
                child.destroy()

        month_index = list(calendar.month_name).index(self.month_var.get())
        year = int(self.year_var.get())

        cal = calendar.Calendar(firstweekday=0)
        month_weeks = cal.monthdayscalendar(year, month_index)

        self.day_btns.clear()
        row_offset = 1  # Row 0 holds weekday labels
        # Configure row weights so they expand evenly
        for r in range(len(month_weeks)):
            self.grid_frame.rowconfigure(r + row_offset, weight=1)
        for r, week in enumerate(month_weeks):
            for c, day in enumerate(week):
                if day == 0:
                    # Empty day (belongs to previous/next month)
                    tk.Label(self.grid_frame, text="", bg="#e8f4ff", bd=0, highlightthickness=0).grid(
                        row=r + row_offset, column=c, padx=3, pady=3
                    )
                    continue

                # Prepare button label: show day number and possibly short event name
                event_data = self.events.get((year, month_index, day))
                display_text = str(day)
                if event_data:
                    if event_data.get('choice'):
                        display_text += f"\n{event_data['choice']}"
                    note_text = event_data.get('note')
                    if note_text:
                        display_text += f"\n\n{note_text}"

                btn = tk.Button(
                    self.grid_frame,
                    text=display_text,
                    bg="#e8f4ff",
                    activebackground="#d2e7ff",
                    font=self.day_font,
                    relief=tk.FLAT,
                    bd=0,
                    highlightthickness=0,
                    command=lambda d=day: self.open_event_dialog(d),
                    anchor="nw",
                    justify="left",
                    wraplength=120,
                )
                btn.grid(row=r + row_offset, column=c, padx=1, pady=1, sticky="NSEW")

                # Highlight if an event already exists
                if event_data:
                    btn.configure(bg="lightblue")
                self.day_btns[(r, c)] = btn

    def clear_month(self) -> None:
        """Erase all entries in the currently selected month after user confirmation."""
        month_index = list(calendar.month_name).index(self.month_var.get())
        year = int(self.year_var.get())
        if not messagebox.askyesno("Clear Month", f"Erase all entries for {self.month_var.get()} {year}?"):
            return
        keys_to_remove = [k for k in self.events if k[0] == year and k[1] == month_index]
        for k in keys_to_remove:
            del self.events[k]
        self._save_events()
        self.draw_calendar()

    def open_event_dialog(self, day: int) -> None:
        """Open a small window with a drop-down to assign an event to a day."""
        month_index = list(calendar.month_name).index(self.month_var.get())
        year = int(self.year_var.get())
        key: DateKey = (year, month_index, day)

        dialog = tk.Toplevel(self.root)
        dialog.title(f"Add item – {day} {self.month_var.get()} {year}")
        dialog.grab_set()  # Make modal

        ttk.Label(dialog, text="Select item to add:").grid(row=0, column=0, padx=10, pady=10)

        existing = self.events.get(key)
        sel_var = tk.StringVar(value=(existing.get("choice") if existing else EVENT_CHOICES[0]))
        combo = ttk.Combobox(dialog, values=EVENT_CHOICES, textvariable=sel_var, state="readonly")
        combo.grid(row=1, column=0, padx=10)

        # Additional note entry
        ttk.Label(dialog, text="Additional notes:").grid(row=2, column=0, padx=10, pady=(10,0))
        note_text = tk.Text(dialog, width=30, height=3)
        if existing and existing.get("note"):
            note_text.insert("1.0", existing["note"])
        note_text.grid(row=3, column=0, padx=10)

        def save_and_close() -> None:
            self.events[key] = {"choice": sel_var.get(), "note": note_text.get("1.0", "end-1c")}
            self._save_events()
            dialog.destroy()
            self.draw_calendar()

        ttk.Button(dialog, text="Save", command=save_and_close).grid(
            row=4, column=0, pady=(10, 5)
        )
        ttk.Button(dialog, text="Cancel", command=dialog.destroy).grid(row=5, column=0, pady=(0, 10))

        dialog.columnconfigure(0, weight=1)

    # ------------------------------------------------------------------
    # --------------------------------------------------------------
    # Persistence helpers
    # --------------------------------------------------------------
    def _load_events(self) -> None:
        """Load events from JSON file if it exists."""
        if self._data_file.exists():
            try:
                data = json.loads(self._data_file.read_text())
                for iso_str, value in data.items():
                    y, m, d = map(int, iso_str.split("-"))
                    # Backward compatibility: older versions stored a plain string
                    if isinstance(value, str):
                        self.events[(y, m, d)] = {"choice": value, "note": ""}
                    else:
                        self.events[(y, m, d)] = value
            except Exception:
                # Corrupt file – ignore
                pass

    def _save_events(self) -> None:
        """Persist events to JSON (simple mapping of ISO date string -> label)."""
        data = {f"{y}-{m}-{d}": value for (y, m, d), value in self.events.items()}
        try:
            self._data_file.write_text(json.dumps(data, indent=2))
        except Exception:
            pass  # Silently ignore write errors for now

    # --------------------------------------------------------------
    def run(self) -> None:
        self.root.mainloop()


if __name__ == "__main__":
    try:
        CalendarApp().run()
    except KeyboardInterrupt:
        sys.exit(0)
