import os
import yfinance as yf
import pandas as pd

STOCKS = ["AAPL", "TSLA", "MSFT", "NVDA", "AMZN", "GOOGL", "META", "JPM", "V", "SPY"]
START_DATE = "2018-01-01"
END_DATE = "2026-04-29"

OUTPUT_PATH = "data/raw/historical_stock_data.csv"

os.makedirs("data/raw", exist_ok=True)

all_data = []

for ticker in STOCKS:
    print(f"Downloading {ticker}...")

    df = yf.download(
        ticker,
        start=START_DATE,
        end=END_DATE,
        auto_adjust=False,
        progress=False
    )

    df = df.reset_index()

    # Fix multi-level columns if yfinance returns them
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [col[0] if col[0] else col[1] for col in df.columns]

    df["asset"] = ticker
    df["asset_type"] = "Stock"

    df = df.rename(columns={
        "Date": "timestamp",
        "Open": "open",
        "High": "high",
        "Low": "low",
        "Close": "close",
        "Adj Close": "adjusted_close",
        "Volume": "volume"
    })

    df = df[[
        "timestamp",
        "asset",
        "asset_type",
        "open",
        "high",
        "low",
        "close",
        "adjusted_close",
        "volume"
    ]]

    all_data.append(df)

final_df = pd.concat(all_data, ignore_index=True)

final_df.to_csv(OUTPUT_PATH, index=False)

print(f"\nHistorical stock data saved to {OUTPUT_PATH}")
print(f"Total rows collected: {len(final_df)}")
print(f"Total assets collected: {final_df['asset'].nunique()}")
print(final_df.head())
print(final_df.tail())