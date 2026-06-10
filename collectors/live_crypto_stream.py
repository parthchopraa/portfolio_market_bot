import json
import sqlite3
from websocket import WebSocketApp
from datetime import datetime

DB_PATH = "data/database/market_data.db"

STREAMS = [
    "btcusdt@trade",
    "ethusdt@trade",
    "solusdt@trade"
]

SOCKET_URL = f"wss://stream.binance.com:9443/stream?streams={'/'.join(STREAMS)}"

print("Connecting to Binance WebSocket...")

# Database connection
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
        "Binance"
    ))

    conn.commit()

def on_message(ws, message):

    try:
        data = json.loads(message)

        trade_data = data["data"]

        symbol = trade_data["s"]
        price = float(trade_data["p"])
        quantity = float(trade_data["q"])

        asset = symbol.replace("USDT", "")

        print(f"{asset} | Price: {price} | Qty: {quantity}")

        save_trade(asset, price, quantity)

    except Exception as e:
        print("Message Error:", e)

def on_error(ws, error):
    print("WebSocket Error:", error)

def on_close(ws, close_status_code, close_msg):
    print("WebSocket Closed")

def on_open(ws):
    print("WebSocket Connection Opened")

ws = WebSocketApp(
    SOCKET_URL,
    on_open=on_open,
    on_message=on_message,
    on_error=on_error,
    on_close=on_close
)

ws.run_forever()