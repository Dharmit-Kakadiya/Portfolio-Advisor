import sqlite3
conn = sqlite3.connect('investment_advisor.db')
cursor = conn.cursor()
try:
    cursor.execute(f"SELECT * FROM portfolios;")
    rows = cursor.fetchall()
    if rows:
        col_names = [data[0] for data in cursor.description]
        print(" | ".join(col_names))
        print("-" * (len(" | ".join(col_names)) + 10))
        for row in rows:
            print(" | ".join(str(item) for item in row))
    else:
        print(f"No data found in table.")

    print("----------------------------------------------------------------------------------------------------------------------------")
    cursor.execute(f"SELECT * FROM users;")
    rows = cursor.fetchall()
    if rows:
        col_names = [data[0] for data in cursor.description]
        print(" | ".join(col_names))
        print("-" * (len(" | ".join(col_names)) + 10))
        for row in rows:
            print(" | ".join(str(item) for item in row))
    else:
        print(f"No data found in table.")
except sqlite3.Error as e:
    print(f"An error occurred: {e}")
# Run this code directy in VS CODE 