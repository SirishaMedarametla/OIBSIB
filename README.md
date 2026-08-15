Oasis Infobyte Internship Projects

🧮 BMI Calculator (Task 2 - Oasis Infobyte Internship)
📌 Objective
Build a Python program that calculates a user's Body Mass Index (BMI) and classifies it into health categories.

Beginner Tier → Command-line tool
Advanced Tier → Full GUI application with data persistence and trend visualization
⚙️ Tech Stack
Beginner: Python, input(), basic arithmetic
Advanced: Python, tkinter (or PyQt5), matplotlib, sqlite3 / CSV
✅ Features
Beginner Tier
Prompt user for weight (kg) and height (m) via command line
Calculate BMI using formula: BMI = weight / (height²)
Classify result into categories:
Underweight (< 18.5)
Normal (18.5–24.9)
Overweight (25–29.9)
Obese (≥ 30)
Display BMI rounded to 2 decimal places
Input validation for non-numeric or negative values
Advanced Tier
GUI window built with tkinter
Input fields + "Calculate" button
Result displayed with color-coded feedback
Multi-user support (save BMI records for different users)
Historical records stored in SQLite database
Graph view: BMI trend over time using matplotlib
Error handling for database read/write failures
🚀 How to Run
Beginner (Command Line)
python bmi_calculator.py
