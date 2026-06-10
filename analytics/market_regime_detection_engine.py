import os
import pandas as pd
import numpy as np

INPUT_PATH = "data/processed/market_features.csv"

OUTPUT_PATH = "data/processed/market_regime_summary.csv"
HISTORICAL_OUTPUT_PATH = "data/processed/historical_market_regimes.csv"

os.makedirs("data/processed", exist_ok=True)

print("Loading market features...")
df = pd.read_csv(INPUT_PATH)

df["timestamp"] = pd.to_datetime(df["timestamp"])
df = df.sort_values(["asset", "timestamp"]).reset_index(drop=True)

all_regime_rows = []
summary_rows = []

for asset, asset_df in df.groupby("asset"):
    print(f"Detecting regimes for {asset}...")

    asset_df = asset_df.sort_values("timestamp").copy()

    # Rolling regime inputs
    asset_df["rolling_return_30"] = asset_df["daily_return"].rolling(30).mean() * 252
    asset_df["rolling_volatility_30"] = asset_df["daily_return"].rolling(30).std() * np.sqrt(252)
    asset_df["rolling_return_90"] = asset_df["daily_return"].rolling(90).mean() * 252
    asset_df["rolling_volatility_90"] = asset_df["daily_return"].rolling(90).std() * np.sqrt(252)

    asset_df["price_above_ma30"] = asset_df["close"] > asset_df["ma_30"]

    regimes = []

    for _, row in asset_df.iterrows():

        regime = "Unknown"

        r30 = row["rolling_return_30"]
        v30 = row["rolling_volatility_30"]
        r90 = row["rolling_return_90"]
        above_ma = row["price_above_ma30"]

        if pd.isna(r30) or pd.isna(v30) or pd.isna(r90):
            regimes.append(regime)
            continue

        # Regime logic
        if v30 > 0.80:
            regime = "High Volatility Regime"
        elif r30 > 0.20 and r90 > 0.10 and above_ma:
            regime = "Bullish Regime"
        elif r30 < -0.20 and r90 < -0.10 and not above_ma:
            regime = "Bearish Regime"
        elif abs(r30) < 0.10 and v30 < 0.30:
            regime = "Stable / Sideways Regime"
        elif abs(r30) < 0.10:
            regime = "Sideways Regime"
        else:
            regime = "Mixed Regime"

        regimes.append(regime)

    asset_df["market_regime"] = regimes

    latest = asset_df.dropna(subset=["market_regime"]).iloc[-1]

    summary_rows.append({
        "asset": asset,
        "asset_type": latest["asset_type"],
        "latest_date": latest["timestamp"],
        "latest_close": latest["close"],
        "rolling_return_30": latest["rolling_return_30"],
        "rolling_volatility_30": latest["rolling_volatility_30"],
        "rolling_return_90": latest["rolling_return_90"],
        "rolling_volatility_90": latest["rolling_volatility_90"],
        "market_regime": latest["market_regime"]
    })

    all_regime_rows.append(asset_df[[
        "timestamp",
        "asset",
        "asset_type",
        "close",
        "rolling_return_30",
        "rolling_volatility_30",
        "rolling_return_90",
        "rolling_volatility_90",
        "market_regime"
    ]])

historical_regimes_df = pd.concat(all_regime_rows, ignore_index=True)
summary_df = pd.DataFrame(summary_rows)

historical_regimes_df.to_csv(HISTORICAL_OUTPUT_PATH, index=False)
summary_df.to_csv(OUTPUT_PATH, index=False)

print("\nMarket regime detection completed.")
print(f"Historical regimes saved to: {HISTORICAL_OUTPUT_PATH}")
print(f"Current regime summary saved to: {OUTPUT_PATH}")

print("\nCurrent Market Regimes:")
print(summary_df[[
    "asset",
    "asset_type",
    "rolling_return_30",
    "rolling_volatility_30",
    "market_regime"
]])