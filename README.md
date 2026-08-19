🧮 BMI Calculator (Task 2 - Oasis Infobyte Internship)
📌 Objective
Build a Python program that calculates a user's Body Mass Index (BMI), classifies it into health categories, and stores historical records for multi-user tracking.

⚙️ Tech Stack
Beginner Tier: Python, input(), basic arithmetic

Advanced Tier: Python, tkinter, matplotlib, sqlite3

✅ Features
Beginner Tier
Command-line tool using input()

BMI calculation: BMI = weight / (height²)

Health categories:

Underweight (< 18.5)

Normal (18.5–24.9)

Overweight (25–29.9)

Obese (≥ 30)

Input validation for non-numeric or negative values

Displays BMI rounded to 2 decimal places

Advanced Tier
GUI window built with tkinter

Input fields for username, weight, and height

Calculate BMI button with color-coded feedback:

Green → Normal

Orange → Underweight / Overweight

Red → Obese

Multi-user support (records saved per username)

Historical records stored in SQLite database

Show Trend button → plots BMI history using matplotlib

Error handling for invalid inputs and database failures

Confirmation popup when record is saved successfully

📂 Database Details
Database file: bmi_records.db

Table: bmi_records

id → Auto-increment primary key

username → User identifier

bmi → Calculated BMI

category → Health category

timestamp → Auto-generated date/time

🚀 How to Run
Beginner (Command Line)
bash
python bmi_calculator.py
Advanced (GUI Application)
bash
python advanced_bmi_calculator.py
📊 Example Output
BMI result shown in GUI with color feedback

Trend chart displaying BMI progression over time

Records saved in SQLite and can be viewed with:

bash
sqlite3 bmi_records.db
.tables
.headers on
.mode column
SELECT * FROM bmi_records;
