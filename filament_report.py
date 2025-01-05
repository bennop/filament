import sqlite3
import matplotlib.pyplot as plt
import random
from datetime import datetime, timedelta

# Connect to SQLite database
conn = sqlite3.connect("filaments.db")
cursor = conn.cursor()

def get_filament_data():
    """Retrieve filament data for the past year (or the full dataset if shorter)."""
    one_year_ago = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
    cursor.execute("""
    SELECT maker, type, color, weight, date FROM filaments
    WHERE date >= ?
    ORDER BY date ASC
    """, (one_year_ago,))
    return cursor.fetchall()

def assign_markers_by_subtype(types):
    """Assign unique markers to each filament subtype (type)."""
    markers = ['o', '^', 's', '*', 'D', 'v', '<', '>', 'P', 'X', 'h']
    marker_map = {}
    for ftype in types:
        marker_map[ftype] = random.choice(markers)
    return marker_map

def plot_filament_usage(data):
    """Generate a graph of filament usage."""
    filaments = {}
    unique_subtypes = set()

    # Organize data and collect unique filament subtypes
    for maker, ftype, color, weight, date in data:
        key = (maker, ftype, color)
        if key not in filaments:
            filaments[key] = {"dates": [], "weights": [], "color": color, "type": ftype}
        filaments[key]["dates"].append(datetime.strptime(date, "%Y-%m-%d"))
        filaments[key]["weights"].append(weight)
        unique_subtypes.add(ftype)

    # Assign markers to filament subtypes
    marker_map = assign_markers_by_subtype(unique_subtypes)

    plt.figure(figsize=(12, 6))
    for (maker, ftype, color), values in filaments.items():
        dates = values["dates"]
        weights = values["weights"]
        line_color = color.lower()  # Use the color name directly
        marker = marker_map[ftype]  # Use marker based on the filament subtype

        # Special style for white filament
        if color.lower() == "white":
            if len(dates) == 1:
                plt.scatter(dates, weights, label=f"{maker} {ftype} ({color})", 
                            edgecolor="black", facecolor="white", s=100, marker=marker, zorder=3)
            else:
                plt.plot(dates, weights, label=f"{maker} {ftype} ({color})", 
                         linestyle="dotted", color="grey", marker=marker, 
                         markeredgecolor="black", markerfacecolor="white", zorder=3)
        else:
            # Regular plotting for other colors
            if len(dates) == 1:
                plt.scatter(dates, weights, label=f"{maker} {ftype} ({color})", 
                            color=line_color, s=100, marker=marker)
            else:
                plt.plot(dates, weights, label=f"{maker} {ftype} ({color})", 
                         color=line_color, marker=marker)

    plt.title("Filament Usage (Last Year)", fontsize=16)
    plt.xlabel("Date", fontsize=14)
    plt.ylabel("Weight (grams)", fontsize=14)
    plt.xticks(rotation=45)
    plt.grid(True, linestyle="--", alpha=0.7)
    plt.legend(fontsize=10)
    plt.tight_layout()
    plt.savefig("filament_usage_report.png")
    plt.show()

if __name__ == "__main__":
    data = get_filament_data()
    if not data:
        print("No filament data available in the database for the past year.")
    else:
        plot_filament_usage(data)
