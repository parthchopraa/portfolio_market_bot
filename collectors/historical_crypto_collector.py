import os
import time
import requests
import pandas as pd
from datetime import datetime, timezone

CRYPTO_SYMBOLS = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT"]

START_DATE = "2018-01-01"
OUTPUT_PATH = "data/raw/historical_crypto_data.csv"

os.makedirs("data/raw", exist_ok=True)

def date_to_milliseconds(date_str):
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    dt = dt.replace(tzinfo=timezone.utc)
    return int(dt.timestamp() * 1000)

def get_binance_klines(symbol, start_date):
    url = "https://api.binance.com/api/v3/klines"

    start_time = date_to_milliseconds(start_date)
    all_rows = []

    while True:
        params = {
            "symbol": symbol,
            "interval": "1d",
            "startTime": start_time,
            "limit": 1000
        }

        response = requests.get(url, params=params, timeout=30)
        print(symbol, "Status Code:", response.status_code)
        response.raise_for_status()

        data = response.json()

        if not data:
            break

        all_rows.extend(data)

        last_open_time = data[-1][0]
        start_time = last_open_time + 24 * 60 * 60 * 1000

        time.sleep(0.5)

        if len(data) < 1000:
            break

    return all_rows

all_data = []

for symbol in CRYPTO_SYMBOLS:
    print(f"\nDownloading {symbol}...")

    try:
        rows = get_binance_klines(symbol, START_DATE)

        df = pd.DataFrame(rows, columns=[
            "open_time", "open", "high", "low", "close", "volume",
            "close_time", "quote_asset_volume", "number_of_trades",
            "taker_buy_base_volume", "taker_buy_quote_volume", "ignore"
        ])

        df["timestamp"] = pd.to_datetime(df["open_time"], unit="ms")
        df["asset"] = symbol.replace("USDT", "")
        df["asset_type"] = "Cryptocurrency"

        numeric_cols = ["open", "high", "low", "close", "volume"]
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors="coerce")

        df["adjusted_close"] = df["close"]
        df["market_cap"] = None

        df = df[[
            "timestamp",
            "asset",
            "asset_type",
            "open",
            "high",
            "low",
            "close",
            "adjusted_close",
            "volume",
            "market_cap"
        ]]

        all_data.append(df)

        print(f"{symbol} rows collected: {len(df)}")

    except Exception as e:
        print(f"Error collecting {symbol}: {e}")

if len(all_data) == 0:
    print("\nNo crypto data collected.")
else:
    final_df = pd.concat(all_data, ignore_index=True)
    final_df.to_csv(OUTPUT_PATH, index=False)

    print(f"\nHistorical crypto data saved to {OUTPUT_PATH}")
    print(f"Total rows collected: {len(final_df)}")
    print(f"Total crypto assets collected: {final_df['asset'].nunique()}")
    print(final_df.head())
    print(final_df.tail())