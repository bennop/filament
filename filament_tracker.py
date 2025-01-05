import sqlite3
import sys
from datetime import datetime

# Connect to SQLite database
conn = sqlite3.connect("filaments.db")
cursor = conn.cursor()

# Create the filaments table
cursor.execute("""
CREATE TABLE IF NOT EXISTS filaments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    maker TEXT NOT NULL,
    type TEXT NOT NULL,
    color TEXT NOT NULL,
    weight REAL NOT NULL,
    date TEXT DEFAULT CURRENT_DATE
)
""")
conn.commit()

def validate_date(date_str):
    """Validate and parse a date string. Return None if invalid."""
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").strftime("%Y-%m-%d")
    except ValueError:
        return None

def find_best_match(maker, ftype, color):
    """Find the best match for the given criteria."""
    query = """
    SELECT maker, type, color FROM filaments
    WHERE (? IS NULL OR maker = ?) AND (? IS NULL OR type = ?) AND (? IS NULL OR color = ?)
    ORDER BY
        (CASE WHEN maker = ? THEN 1 ELSE 0 END +
         CASE WHEN type = ? THEN 1 ELSE 0 END +
         CASE WHEN color = ? THEN 1 ELSE 0 END) DESC,
        id DESC
    LIMIT 1
    """
    cursor.execute(query, (maker, maker, ftype, ftype, color, color, maker, ftype, color))
    return cursor.fetchone()

def add_filament_entry(args):
    """Add a new filament entry."""
    if len(args) < 1:
        print("Error: At least the weight must be provided.")
        return

    # Check if the last argument is a valid date
    possible_date = args[-1]
    date = validate_date(possible_date)
    
    # If no valid date is found, assume weight is the last argument
    if date:
        weight_arg_index = len(args) - 2
    else:
        weight_arg_index = len(args) - 1
        date = datetime.now().strftime("%Y-%m-%d")

    # Extract and validate weight
    try:
        weight = float(args[weight_arg_index])
    except (ValueError, IndexError):
        print("Error: Weight must be a numeric value.")
        return

    # Extract optional maker, type, and color
    maker, ftype, color = None, None, None
    if weight_arg_index > 0:
        optional_args = args[:weight_arg_index]
        maker, ftype, color = optional_args + [None] * (3 - len(optional_args))

    # Find the best match
    match = find_best_match(maker, ftype, color)
    if match:
        maker = maker or match[0]
        ftype = ftype or match[1]
        color = color or match[2]

    if not maker or not ftype or not color:
        print("Error: Could not infer all required values. Please specify more details.")
        return

    # Insert the new entry
    cursor.execute("""
    INSERT INTO filaments (maker, type, color, weight, date)
    VALUES (?, ?, ?, ?, ?)
    """, (maker, ftype, color, weight, date))
    conn.commit()
    print(f"Entry added: {maker}, {ftype}, {color}, {weight}g on {date}")

if __name__ == "__main__":
    # Process all arguments
    args = sys.argv[1:]
    add_filament_entry(args)
    conn.close()
