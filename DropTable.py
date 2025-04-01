import sqlite3
conn = sqlite3.connect('investment_advisor.db')
cursor = conn.cursor()
try:
    cursor.execute(f"DROP table portfolios")
    cursor.execute(f"DROP table users")
except sqlite3.Error as e:
    print(f"An error occurred: {e}")
# Run this code directy in VS CODE 