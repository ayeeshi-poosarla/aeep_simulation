import sqlite3
import pandas as pd

# Let's assume this is the processed DataFrame from earlier
def get_dashboard_df():
    return pd.DataFrame([{
        'time_sec': 520,
        'time_score': 92.3,
        'enucleated_mass': 18.5,
        'mass_score': 88.0,
        'force_violations': 7,
        'force_score': 28.6,
        'path_length': 153.2,
        'path_score': 91.3,
        'idle_time': 12.4,
        'idle_score': 40.3,
        'overall_score': 68.7
    }])

# Connect to SQLite database (or create it if it doesn't exist)
conn = sqlite3.connect("aeep_dashboard.db")
cursor = conn.cursor()

# Create table if it doesn't exist
cursor.execute("""
CREATE TABLE IF NOT EXISTS dashboard_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    time_sec REAL,
    time_score REAL,
    enucleated_mass REAL,
    mass_score REAL,
    force_violations INTEGER,
    force_score REAL,
    path_length REAL,
    path_score REAL,
    idle_time REAL,
    idle_score REAL,
    overall_score REAL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")

# Insert data from DataFrame
df = get_dashboard_df()
df.to_sql("dashboard_metrics", conn, if_exists='append', index=False)

# Confirm and close
conn.commit()
conn.close()

print("Data saved to aeep_dashboard.db ✅")
