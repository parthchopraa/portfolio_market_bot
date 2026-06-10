import pandas as pd
import os

STOCK_PATH = "data/raw/historical_stock_data.csv"
CRYPTO_PATH = "data/raw/historical_crypto_data.csv"

OUTPUT_PATH = "data/processed/combined_historical_market_data.csv"

os.makedirs("data/processed", exist_ok=True)

print("Loading stock data...")
stocks_df = pd.read_csv(STOCK_PATH)

print("Loading crypto data...")
crypto_df = pd.read_csv(CRYPTO_PATH)

# Standardize timestamp
stocks_df["timestamp"] = pd.to_datetime(stocks_df["timestamp"])
crypto_df["timestamp"] = pd.to_datetime(crypto_df["timestamp"])

# Ensure same columns
required_columns = [
    "timestamp",
    "asset",
    "asset_type",
    "open",
    "high",
    "low",
    "close",
    "adjusted_close",
    "volume"
]

stocks_df = stocks_df[required_columns]
crypto_df = crypto_df[required_columns]

# Merge
combined_df = pd.concat(
    [stocks_df, crypto_df],
    ignore_index=True
)

# Remove duplicates
combined_df = combined_df.drop_duplicates()

# Sort
combined_df = combined_df.sort_values(
    by=["timestamp", "asset"]
)

# Reset index
combined_df = combined_df.reset_index(drop=True)

# Save
combined_df.to_csv(OUTPUT_PATH, index=False)

print("\nCombined dataset created successfully.")
print(f"Total rows: {len(combined_df)}")
print(f"Assets included: {combined_df['asset'].nunique()}")

print("\nAssets:")
print(combined_df["asset"].unique())

print("\nDate Range:")
print(combined_df["timestamp"].min())
print(combined_df["timestamp"].max())

print("\nPreview:")
print(combined_df.head())