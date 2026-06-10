import os
import pandas as pd
import numpy as np

INPUT_PATH = "data/processed/market_features.csv"
OUTPUT_PATH = "data/processed/market_comparison_summary.csv"
ASSET_OUTPUT_PATH = "data/processed/asset_risk_summary.csv"

os.makedirs("data/processed", exist_ok=True)

print("Loading market features...")
df = pd.read_csv(INPUT_PATH)
df["timestamp"] = pd.to_datetime(df["timestamp"])

# Remove rows where return is missing
df = df.dropna(subset=["daily_return"])

risk_free_rate = 0.02 / 252  # Approx daily risk-free rate assuming 2% annual

asset_summaries = []

for asset, asset_df in df.groupby("asset"):
    asset_df = asset_df.sort_values("timestamp").copy()

    avg_daily_return = asset_df["daily_return"].mean()
    annual_return = avg_daily_return * 252
    annual_volatility = asset_df["daily_return"].std() * np.sqrt(252)

    sharpe_ratio = (
        (avg_daily_return - risk_free_rate) / asset_df["daily_return"].std()
        if asset_df["daily_return"].std() != 0
        else np.nan
    ) * np.sqrt(252)

    max_drawdown = asset_df["drawdown"].min()

    latest_close = asset_df["close"].iloc[-1]
    latest_ma_30 = asset_df["ma_30"].iloc[-1]
    latest_volatility_30 = asset_df["volatility_30"].iloc[-1]

    # Risk score logic: 1 = low risk, 10 = high risk
    risk_score = 1

    if annual_volatility > 0.25:
        risk_score += 2
    if annual_volatility > 0.50:
        risk_score += 2
    if max_drawdown < -0.30:
        risk_score += 2
    if max_drawdown < -0.60:
        risk_score += 2
    if latest_volatility_30 > 0.04:
        risk_score += 1

    risk_score = min(risk_score, 10)

    if risk_score <= 3:
        risk_category = "Low Risk"
    elif risk_score <= 6:
        risk_category = "Moderate Risk"
    else:
        risk_category = "High Risk"

    # Basic market stance
    if latest_close > latest_ma_30 and avg_daily_return > 0:
        market_stance = "Positive Trend"
    elif latest_close < latest_ma_30 and avg_daily_return < 0:
        market_stance = "Weak Trend"
    else:
        market_stance = "Mixed / Neutral"

    asset_summaries.append({
        "asset": asset,
        "asset_type": asset_df["asset_type"].iloc[0],
        "start_date": asset_df["timestamp"].min(),
        "end_date": asset_df["timestamp"].max(),
        "latest_close": latest_close,
        "annual_return": annual_return,
        "annual_volatility": annual_volatility,
        "sharpe_ratio": sharpe_ratio,
        "max_drawdown": max_drawdown,
        "risk_score": risk_score,
        "risk_category": risk_category,
        "market_stance": market_stance
    })

asset_summary_df = pd.DataFrame(asset_summaries)

# Group comparison: Stock vs Crypto
comparison_df = asset_summary_df.groupby("asset_type").agg({
    "annual_return": "mean",
    "annual_volatility": "mean",
    "sharpe_ratio": "mean",
    "max_drawdown": "mean",
    "risk_score": "mean"
}).reset_index()

asset_summary_df.to_csv(ASSET_OUTPUT_PATH, index=False)
comparison_df.to_csv(OUTPUT_PATH, index=False)

print("\nAsset risk summary created:")
print(ASSET_OUTPUT_PATH)

print("\nMarket comparison summary created:")
print(OUTPUT_PATH)

print("\nStock vs Crypto Comparison:")
print(comparison_df)

print("\nAsset-Level Risk Summary:")
print(asset_summary_df)