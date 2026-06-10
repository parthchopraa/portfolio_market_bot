import sqlite3
import os

DB_PATH = "data/database/market_data.db"

os.makedirs("data/database", exist_ok=True)

conn = sqlite3.connect(DB_PATH)

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS live_market_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    asset TEXT,
    price REAL,
    quantity REAL,
    source TEXT
)
""")

conn.commit()
conn.close()

print("Database initialized successfully.")