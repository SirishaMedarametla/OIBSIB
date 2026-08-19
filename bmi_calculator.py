"""
Advanced BMI Calculator - Task 2
Author: Varsha Nalajala
Description: GUI BMI calculator with SQLite storage and trend visualization.
"""

import tkinter as tk
from tkinter import messagebox
import sqlite3
import matplotlib.pyplot as plt
import datetime
import os

# --- Database Setup ---
def init_db():
    db_path = os.path.abspath("bmi_records.db")
    print("Using database at:", db_path)  # Debug: shows exact file path
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bmi_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            bmi REAL,
            category TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

# --- BMI Logic ---
def calculate_bmi(weight, height):
    return weight / (height ** 2)

def get_category(bmi):
    if bmi < 18.5:
        return "Underweight"
    elif 18.5 <= bmi < 24.9:
        return "Normal"
    elif 25 <= bmi < 29.9:
        return "Overweight"
    else:
        return "Obese"

# --- GUI Actions ---
def on_calculate():
    try:
        username = entry_user.get().strip()
        weight = float(entry_weight.get())
        height = float(entry_height.get())

        if not username:
            messagebox.showerror("Error", "Please enter a username.")
            return
        if weight <= 0 or height <= 0:
            messagebox.showerror("Error", "Weight and height must be positive.")
            return

        bmi = calculate_bmi(weight, height)
        category = get_category(bmi)

        # Save to DB safely
        try:
            with sqlite3.connect("bmi_records.db") as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO bmi_records (username, bmi, category) VALUES (?, ?, ?)",
                    (username, bmi, category)
                )
                conn.commit()
            print("Saved:", username, f"{bmi:.2f}", category)  # Debug print
            messagebox.showinfo("Success", "Record saved successfully!")
        except Exception as e:
            messagebox.showerror("Database Error", str(e))
            return

        # Display result with color feedback
        result_label.config(text=f"BMI: {bmi:.2f} ({category})")
        if category == "Normal":
            result_label.config(fg="green")
        elif category == "Obese":
            result_label.config(fg="red")
        else:
            result_label.config(fg="orange")

    except ValueError:
        messagebox.showerror("Error", "Please enter valid numeric values.")

def show_trend():
    username = entry_user.get().strip()
    if not username:
        messagebox.showerror("Error", "Enter a username to view trend.")
        return

    try:
        with sqlite3.connect("bmi_records.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT timestamp, bmi FROM bmi_records WHERE username=? ORDER BY timestamp", (username,))
            records = cursor.fetchall()

        if not records:
            messagebox.showinfo("No Data", "No records found for this user.")
            return

        # Convert timestamps to datetime objects for cleaner plotting
        dates = [datetime.datetime.fromisoformat(r[0]) for r in records]
        bmis = [r[1] for r in records]

        plt.figure(figsize=(8, 4))
        plt.plot(dates, bmis, marker="o", linestyle="-", color="blue")
        plt.title(f"BMI Trend for {username}")
        plt.xlabel("Date")
        plt.ylabel("BMI")
        plt.gcf().autofmt_xdate()  # auto-format x-axis labels
        plt.tight_layout()
        plt.show()

    except Exception as e:
        messagebox.showerror("Database Error", str(e))

# --- GUI Setup ---
init_db()
root = tk.Tk()
root.title("BMI Calculator")

tk.Label(root, text="Username:").grid(row=0, column=0, padx=5, pady=5)
entry_user = tk.Entry(root)
entry_user.grid(row=0, column=1, padx=5, pady=5)

tk.Label(root, text="Weight (kg):").grid(row=1, column=0, padx=5, pady=5)
entry_weight = tk.Entry(root)
entry_weight.grid(row=1, column=1, padx=5, pady=5)

tk.Label(root, text="Height (m):").grid(row=2, column=0, padx=5, pady=5)
entry_height = tk.Entry(root)
entry_height.grid(row=2, column=1, padx=5, pady=5)

tk.Button(root, text="Calculate BMI", command=on_calculate).grid(row=3, column=0, columnspan=2, pady=10)
tk.Button(root, text="Show Trend", command=show_trend).grid(row=4, column=0, columnspan=2, pady=10)

result_label = tk.Label(root, text="", font=("Arial", 12))
result_label.grid(row=5, column=0, columnspan=2, pady=10)

root.mainloop()