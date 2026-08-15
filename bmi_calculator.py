"""
BMI Calculator - Advanced Tier (GUI Application)
--------------------------------------------------
Tech: tkinter (GUI), sqlite3 (persistence), matplotlib (trend chart)

Features:
  - GUI window with labeled input fields and a Calculate button
  - Colour-coded result feedback (green/yellow/orange/red)
  - Multi-user support: BMI records saved per named user
  - Historical records stored in an SQLite database
  - Graph view: matplotlib line chart of a user's BMI trend over time
  - Error handling for database read/write failures
"""

import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

DB_PATH = "bmi_records.db"


# ----------------------------------------------------------------------
# Database layer
# ----------------------------------------------------------------------
class BMIDatabase:
    """Handles all SQLite persistence for BMI records."""

    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._init_db()

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        try:
            with self._connect() as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS records (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_name TEXT NOT NULL,
                        weight REAL NOT NULL,
                        height REAL NOT NULL,
                        bmi REAL NOT NULL,
                        category TEXT NOT NULL,
                        timestamp TEXT NOT NULL
                    )
                """)
                conn.commit()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Could not initialize database:\n{e}")
            raise

    def add_record(self, user_name, weight, height, bmi, category):
        try:
            with self._connect() as conn:
                conn.execute(
                    "INSERT INTO records (user_name, weight, height, bmi, category, timestamp) "
                    "VALUES (?, ?, ?, ?, ?, ?)",
                    (user_name, weight, height, bmi, category, datetime.now().isoformat(timespec="seconds"))
                )
                conn.commit()
            return True
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to save record:\n{e}")
            return False

    def get_records_for_user(self, user_name):
        try:
            with self._connect() as conn:
                cursor = conn.execute(
                    "SELECT weight, height, bmi, category, timestamp FROM records "
                    "WHERE user_name = ? ORDER BY timestamp ASC",
                    (user_name,)
                )
                return cursor.fetchall()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to read records:\n{e}")
            return []

    def get_all_users(self):
        try:
            with self._connect() as conn:
                cursor = conn.execute("SELECT DISTINCT user_name FROM records ORDER BY user_name ASC")
                return [row[0] for row in cursor.fetchall()]
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to read user list:\n{e}")
            return []


# ----------------------------------------------------------------------
# BMI logic (shared with the CLI version)
# ----------------------------------------------------------------------
def calculate_bmi(weight_kg: float, height_m: float) -> float:
    return weight_kg / (height_m ** 2)


def classify_bmi(bmi: float) -> str:
    if bmi < 18.5:
        return "Underweight"
    elif bmi < 25:
        return "Normal weight"
    elif bmi < 30:
        return "Overweight"
    else:
        return "Obese"


CATEGORY_COLORS = {
    "Underweight": "#3498db",    # blue
    "Normal weight": "#2ecc71",  # green
    "Overweight": "#f39c12",     # orange
    "Obese": "#e74c3c",          # red
}


# ----------------------------------------------------------------------
# GUI Application
# ----------------------------------------------------------------------
class BMIApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("BMI Calculator")
        self.geometry("480x560")
        self.resizable(False, False)
        self.configure(bg="#f4f6f7")

        self.db = BMIDatabase()

        self._build_widgets()

    # ------------------------------------------------------------
    def _build_widgets(self):
        style = ttk.Style(self)
        style.configure("TLabel", background="#f4f6f7", font=("Segoe UI", 11))
        style.configure("Header.TLabel", font=("Segoe UI", 16, "bold"))
        style.configure("TButton", font=("Segoe UI", 11))

        header = ttk.Label(self, text="BMI Calculator", style="Header.TLabel")
        header.pack(pady=(20, 10))

        form = ttk.Frame(self)
        form.pack(pady=5, padx=20, fill="x")

        # User name
        ttk.Label(form, text="User Name:").grid(row=0, column=0, sticky="w", pady=6)
        self.name_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.name_var, width=25).grid(row=0, column=1, pady=6)

        # Weight
        ttk.Label(form, text="Weight (kg):").grid(row=1, column=0, sticky="w", pady=6)
        self.weight_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.weight_var, width=25).grid(row=1, column=1, pady=6)

        # Height
        ttk.Label(form, text="Height (m):").grid(row=2, column=0, sticky="w", pady=6)
        self.height_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.height_var, width=25).grid(row=2, column=1, pady=6)

        # Calculate button
        calc_btn = ttk.Button(self, text="Calculate BMI", command=self.on_calculate)
        calc_btn.pack(pady=15)

        # Result display (colour-coded)
        self.result_frame = tk.Frame(self, bg="#ffffff", height=90, relief="groove", bd=1)
        self.result_frame.pack(fill="x", padx=20, pady=5)
        self.result_frame.pack_propagate(False)

        self.result_label = tk.Label(
            self.result_frame, text="Enter your details and press Calculate",
            bg="#ffffff", font=("Segoe UI", 12), wraplength=420, justify="center"
        )
        self.result_label.pack(expand=True)

        # Action buttons: view history / graph
        action_frame = ttk.Frame(self)
        action_frame.pack(pady=15)

        ttk.Button(action_frame, text="View History", command=self.on_view_history).grid(row=0, column=0, padx=8)
        ttk.Button(action_frame, text="Show Trend Graph", command=self.on_show_graph).grid(row=0, column=1, padx=8)

        # Status bar for validation / error messages
        self.status_var = tk.StringVar(value="")
        status_label = ttk.Label(self, textvariable=self.status_var, foreground="#c0392b")
        status_label.pack(pady=(5, 0))

    # ------------------------------------------------------------
    def _validate_inputs(self):
        """Validate name, weight, height. Returns (name, weight, height) or None on failure."""
        name = self.name_var.get().strip()
        weight_raw = self.weight_var.get().strip()
        height_raw = self.height_var.get().strip()

        if not name:
            self.status_var.set("❌ Please enter a user name.")
            return None

        try:
            weight = float(weight_raw)
        except ValueError:
            self.status_var.set(f"❌ Weight must be a number (got '{weight_raw}').")
            return None

        try:
            height = float(height_raw)
        except ValueError:
            self.status_var.set(f"❌ Height must be a number (got '{height_raw}').")
            return None

        if weight <= 0:
            self.status_var.set("❌ Weight must be a positive number.")
            return None

        if height <= 0:
            self.status_var.set("❌ Height must be a positive number.")
            return None

        if height > 3:
            self.status_var.set("⚠️ Height looks too large for meters (did you mean cm?).")
            return None

        self.status_var.set("")
        return name, weight, height

    # ------------------------------------------------------------
    def on_calculate(self):
        validated = self._validate_inputs()
        if validated is None:
            return

        name, weight, height = validated
        bmi = calculate_bmi(weight, height)
        category = classify_bmi(bmi)
        color = CATEGORY_COLORS.get(category, "#000000")

        self.result_frame.configure(bg=color)
        self.result_label.configure(
            bg=color,
            fg="white",
            text=f"BMI: {round(bmi, 2)}\nCategory: {category}"
        )

        saved = self.db.add_record(name, weight, height, round(bmi, 2), category)
        if saved:
            self.status_var.set(f"✅ Record saved for '{name}'.")
        else:
            self.status_var.set("⚠️ Calculated, but record could not be saved.")

    # ------------------------------------------------------------
    def on_view_history(self):
        name = self.name_var.get().strip()
        if not name:
            messagebox.showinfo("View History", "Enter a user name first, then click View History.")
            return

        records = self.db.get_records_for_user(name)
        if not records:
            messagebox.showinfo("View History", f"No records found for '{name}'.")
            return

        win = tk.Toplevel(self)
        win.title(f"History for {name}")
        win.geometry("480x320")

        columns = ("Weight (kg)", "Height (m)", "BMI", "Category", "Date")
        tree = ttk.Treeview(win, columns=columns, show="headings")
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=90, anchor="center")
        tree.pack(fill="both", expand=True, padx=10, pady=10)

        for weight, height, bmi, category, timestamp in records:
            tree.insert("", "end", values=(weight, height, bmi, category, timestamp.split("T")[0]))

    # ------------------------------------------------------------
    def on_show_graph(self):
        name = self.name_var.get().strip()
        if not name:
            messagebox.showinfo("Trend Graph", "Enter a user name first, then click Show Trend Graph.")
            return

        records = self.db.get_records_for_user(name)
        if len(records) < 2:
            messagebox.showinfo(
                "Trend Graph",
                f"Need at least 2 records for '{name}' to plot a trend. Currently have {len(records)}."
            )
            return

        dates = [r[4].split("T")[0] for r in records]
        bmis = [r[2] for r in records]

        win = tk.Toplevel(self)
        win.title(f"BMI Trend - {name}")
        win.geometry("600x450")

        fig = Figure(figsize=(6, 4.3), dpi=100)
        ax = fig.add_subplot(111)
        ax.plot(dates, bmis, marker="o", color="#2980b9", linewidth=2)
        ax.set_title(f"BMI Trend for {name}")
        ax.set_xlabel("Date")
        ax.set_ylabel("BMI")
        ax.axhspan(18.5, 25, color="#2ecc71", alpha=0.1)  # highlight normal range
        ax.grid(True, linestyle="--", alpha=0.5)
        fig.autofmt_xdate(rotation=45)

        canvas = FigureCanvasTkAgg(fig, master=win)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)


if __name__ == "__main__":
    app = BMIApp()
    app.mainloop()