import time
import sqlite3
import yfinance as yf
from datetime import datetime

DB_PATH = "data/database/market_data.db"

STOCK_SYMBOLS = ["AAPL", "MSFT", "NVDA", "SPY", "TSLA", "GOOGL", "AMZN", "META", "JPM", "V"]

def save_snapshot(asset, price, volume):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO live_market_data (
        timestamp,
        asset,
        price,
        quantity,
        source
    )
    VALUES (?, ?, ?, ?, ?)
    """, (
        datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        asset,
        price,
        volume,
        "yfinance_snapshot"
    ))

    conn.commit()
    conn.close()

def fetch_stock_snapshot(symbol):
    ticker = yf.Ticker(symbol)
    data = ticker.history(period="1d", interval="1m")

    if data.empty:
        data = ticker.history(period="5d", interval="1d")

    if data.empty:
        return None

    latest = data.tail(1)

    return {
        "asset": symbol,
        "price": float(latest["Close"].iloc[0]),
        "volume": float(latest["Volume"].iloc[0])
    }

while True:
    print("\nFetching stock snapshots...")

    for symbol in STOCK_SYMBOLS:
        try:
            result = fetch_stock_snapshot(symbol)

            if result:
                save_snapshot(
                    result["asset"],
                    result["price"],
                    result["volume"]
                )

                print(f"{symbol} | Price: {result['price']} | Volume: {result['volume']}")

            else:
                print(f"No data for {symbol}")

        except Exception as e:
            print(f"Error fetching {symbol}: {e}")

    print("Waiting 60 seconds...")
    time.sleep(60)
    