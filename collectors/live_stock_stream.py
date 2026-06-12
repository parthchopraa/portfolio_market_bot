import json
import sqlite3
from websocket import WebSocketApp
from datetime import datetime

FINNHUB_API_KEY = "d88gjp9r01qq434339ugd88gjp9r01qq434339v0"

DB_PATH = "data/database/market_data.db"

STOCK_SYMBOLS = [
    "AAPL",
    "MSFT",
    "NVDA",
    "SPY",
    "TSLA"
]

SOCKET_URL = f"wss://ws.finnhub.io?token={FINNHUB_API_KEY}"

conn = sqlite3.connect(DB_PATH, check_same_thread=False)
cursor = conn.cursor()

def save_trade(asset, price, quantity):
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

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
        timestamp,
        asset,
        price,
        quantity,
        "Finnhub"
    ))

    conn.commit()

def on_open(ws):
    print("Connected to Finnhub stock stream")

    for symbol in STOCK_SYMBOLS:
        subscribe_message = {
            "type": "subscribe",
            "symbol": symbol
        }

        ws.send(json.dumps(subscribe_message))
        print(f"Subscribed to {symbol}")

def on_message(ws, message):
    try:
        data = json.loads(message)

        if data.get("type") == "trade":
            for trade in data["data"]:
                asset = trade["s"]
                price = float(trade["p"])
                quantity = float(trade["v"])

                print(f"{asset} | Price: {price} | Volume: {quantity}")

                save_trade(asset, price, quantity)

    except Exception as e:
        print("Message error:", e)

def on_error(ws, error):
    print("WebSocket error:", error)

def on_close(ws, close_status_code, close_msg):
    print("Finnhub WebSocket closed")

ws = WebSocketApp(
    SOCKET_URL,
    on_open=on_open,
    on_message=on_message,
    on_error=on_error,
    on_close=on_close
)

ws.run_forever()