import sqlite3
from datetime import datetime

# Connect to SQLite database (or create it if it doesn't exist)
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

def find_best_match(maker, ftype, color):
    """
    Find the best match for the given criteria:
    - Full match (maker, type, color) is preferred.
    - Partial matches are considered if no full match is found.
    Returns the matched record or None if no match is found.
    """
    # Full match query
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

def add_filament_entry(maker=None, ftype=None, color=None, weight=None, date=None):
    """Add a new filament entry with intelligent inference of missing values."""
    # Infer the current date if not provided
    if not date:
        date = datetime.now().strftime("%Y-%m-%d")
    
    # Weight is mandatory
    if weight is None:
        print("Error: Weight is required.")
        return
    
    # Find the best match to infer missing values
    match = find_best_match(maker, ftype, color)
    if match:
        maker = maker or match[0]
        ftype = ftype or match[1]
        color = color or match[2]
    
    # Check if all required fields are now available
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

# Example usage
# Adding a new entry with all values specified
add_filament_entry("Maker", "PLA", "red", 1000, "2025-01-03")

# Adding a new entry with partial values (matches existing entries)
add_filament_entry(None, "PLA", None, 1000)  # Infers "Maker" and "color" as "Maker" and "red"
add_filament_entry(None, None, "red", 500)   # Infers "Maker" and "type" as "Maker" and "PLA"

# Adding a completely new filament
add_filament_entry("Maker2", "PLA", "green", 800)  # No match, uses provided values

# Close the connection
conn.close()
