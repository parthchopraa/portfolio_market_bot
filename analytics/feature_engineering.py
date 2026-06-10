import os
import pandas as pd
import numpy as np

INPUT_PATH = "data/processed/combined_historical_market_data.csv"
OUTPUT_PATH = "data/processed/market_features.csv"

os.makedirs("data/processed", exist_ok=True)

print("Loading combined historical data...")
df = pd.read_csv(INPUT_PATH)

df["timestamp"] = pd.to_datetime(df["timestamp"])

df = df.sort_values(["asset", "timestamp"]).reset_index(drop=True)

feature_frames = []

for asset, asset_df in df.groupby("asset"):
    print(f"Engineering features for {asset}...")

    asset_df = asset_df.copy()
    asset_df = asset_df.sort_values("timestamp")

    # Return features
    asset_df["daily_return"] = asset_df["close"].pct_change()
    asset_df["log_return"] = np.log(asset_df["close"] / asset_df["close"].shift(1))

    # Moving averages
    asset_df["ma_7"] = asset_df["close"].rolling(window=7).mean()
    asset_df["ma_30"] = asset_df["close"].rolling(window=30).mean()

    # Volatility
    asset_df["volatility_7"] = asset_df["daily_return"].rolling(window=7).std()
    asset_df["volatility_30"] = asset_df["daily_return"].rolling(window=30).std()

    # Volume change
    asset_df["volume_change"] = asset_df["volume"].pct_change()

    # Momentum
    asset_df["momentum_7"] = asset_df["close"] - asset_df["close"].shift(7)
    asset_df["momentum_30"] = asset_df["close"] - asset_df["close"].shift(30)

    # Drawdown
    asset_df["rolling_max"] = asset_df["close"].cummax()
    asset_df["drawdown"] = (asset_df["close"] - asset_df["rolling_max"]) / asset_df["rolling_max"]

    # Target for prediction
    asset_df["next_day_return"] = asset_df["daily_return"].shift(-1)

    feature_frames.append(asset_df)

features_df = pd.concat(feature_frames, ignore_index=True)

features_df = features_df.replace([np.inf, -np.inf], np.nan)

features_df.to_csv(OUTPUT_PATH, index=False)

print("\nFeature engineering completed.")
print(f"Saved to: {OUTPUT_PATH}")
print(f"Total rows: {len(features_df)}")
print(f"Total columns: {len(features_df.columns)}")

print("\nColumns:")
print(features_df.columns.tolist())

print("\nPreview:")
print(features_df.head())