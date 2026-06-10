import os
import pandas as pd
import numpy as np

INPUT_PATH = "data/processed/market_technical_indicators.csv"
OUTPUT_PATH = "data/processed/market_signals.csv"

os.makedirs("data/processed", exist_ok=True)

print("Loading technical indicators dataset...")
df = pd.read_csv(INPUT_PATH)

df["timestamp"] = pd.to_datetime(df["timestamp"])
df = df.sort_values(["asset", "timestamp"]).reset_index(drop=True)

signals = []

for asset, asset_df in df.groupby("asset"):
    asset_df = asset_df.sort_values("timestamp").copy()

    latest = asset_df.iloc[-1]

    score = 0
    reasons = []

    # RSI logic
    if latest["rsi_14"] < 30:
        score += 2
        reasons.append("RSI indicates oversold condition")
    elif latest["rsi_14"] > 70:
        score -= 2
        reasons.append("RSI indicates overbought condition")
    else:
        reasons.append("RSI is neutral")

    # MACD logic
    if latest["macd"] > latest["macd_signal"]:
        score += 2
        reasons.append("MACD is bullish")
    elif latest["macd"] < latest["macd_signal"]:
        score -= 2
        reasons.append("MACD is bearish")

    # Moving average trend
    if latest["ema_20"] > latest["ema_50"]:
        score += 1
        reasons.append("Short-term EMA is above long-term EMA")
    elif latest["ema_20"] < latest["ema_50"]:
        score -= 1
        reasons.append("Short-term EMA is below long-term EMA")

    # Price vs VWAP
    if latest["close"] > latest["vwap"]:
        score += 1
        reasons.append("Price is above VWAP")
    elif latest["close"] < latest["vwap"]:
        score -= 1
        reasons.append("Price is below VWAP")

    # Bollinger Band logic
    if latest["close"] < latest["bb_low"]:
        score += 1
        reasons.append("Price is below lower Bollinger Band")
    elif latest["close"] > latest["bb_high"]:
        score -= 1
        reasons.append("Price is above upper Bollinger Band")

    # Momentum logic
    if latest["momentum_7"] > 0:
        score += 1
        reasons.append("7-day momentum is positive")
    elif latest["momentum_7"] < 0:
        score -= 1
        reasons.append("7-day momentum is negative")

    # Volatility penalty
    volatility_30 = latest["volatility_30"]

    if pd.notna(volatility_30):
        if volatility_30 > 0.05:
            score -= 1
            reasons.append("High volatility reduces confidence")
        elif volatility_30 < 0.02:
            score += 1
            reasons.append("Low volatility improves confidence")

    # Final signal
    if score >= 4:
        signal = "BUY"
    elif score <= -4:
        signal = "SELL"
    else:
        signal = "HOLD"

    confidence = min(abs(score) / 8, 1.0)

    if confidence >= 0.75:
        confidence_level = "High"
    elif confidence >= 0.40:
        confidence_level = "Medium"
    else:
        confidence_level = "Low"

    signals.append({
        "timestamp": latest["timestamp"],
        "asset": asset,
        "asset_type": latest["asset_type"],
        "close": latest["close"],
        "signal_score": score,
        "signal": signal,
        "confidence": round(confidence, 2),
        "confidence_level": confidence_level,
        "reason": "; ".join(reasons)
    })

signals_df = pd.DataFrame(signals)

signals_df.to_csv(OUTPUT_PATH, index=False)

print("\nSignal generation completed.")
print(f"Saved to: {OUTPUT_PATH}")

print("\nSignals:")
print(signals_df[[
    "asset",
    "asset_type",
    "close",
    "signal_score",
    "signal",
    "confidence_level"
]])