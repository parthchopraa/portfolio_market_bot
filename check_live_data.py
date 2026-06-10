import sqlite3
import pandas as pd

DB_PATH = "data/database/market_data.db"

conn = sqlite3.connect(DB_PATH)

query = """
SELECT *
FROM live_market_data
ORDER BY id DESC
LIMIT 20
"""

df = pd.read_sql_query(query, conn)

print(df)

conn.close()