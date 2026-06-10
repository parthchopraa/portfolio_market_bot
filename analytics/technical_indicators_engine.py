import os
import pandas as pd
import numpy as np

from ta.momentum import RSIIndicator, StochasticOscillator
from ta.trend import MACD, EMAIndicator
from ta.volatility import BollingerBands, AverageTrueRange
from ta.volume import VolumeWeightedAveragePrice

INPUT_PATH = "data/processed/market_features.csv"
OUTPUT_PATH = "data/processed/market_technical_indicators.csv"

os.makedirs("data/processed", exist_ok=True)

print("Loading market features dataset...")
df = pd.read_csv(INPUT_PATH)

df["timestamp"] = pd.to_datetime(df["timestamp"])

df = df.sort_values(["asset", "timestamp"]).reset_index(drop=True)

indicator_frames = []

for asset, asset_df in df.groupby("asset"):

    print(f"Calculating indicators for {asset}...")

    asset_df = asset_df.copy()

    # RSI
    rsi = RSIIndicator(close=asset_df["close"], window=14)
    asset_df["rsi_14"] = rsi.rsi()

    # MACD
    macd = MACD(close=asset_df["close"])
    asset_df["macd"] = macd.macd()
    asset_df["macd_signal"] = macd.macd_signal()
    asset_df["macd_diff"] = macd.macd_diff()

    # Bollinger Bands
    bollinger = BollingerBands(close=asset_df["close"], window=20)

    asset_df["bb_high"] = bollinger.bollinger_hband()
    asset_df["bb_low"] = bollinger.bollinger_lband()
    asset_df["bb_mid"] = bollinger.bollinger_mavg()

    # EMA
    ema_20 = EMAIndicator(close=asset_df["close"], window=20)
    asset_df["ema_20"] = ema_20.ema_indicator()

    ema_50 = EMAIndicator(close=asset_df["close"], window=50)
    asset_df["ema_50"] = ema_50.ema_indicator()

    # ATR
    atr = AverageTrueRange(
        high=asset_df["high"],
        low=asset_df["low"],
        close=asset_df["close"],
        window=14
    )

    asset_df["atr_14"] = atr.average_true_range()

    # Stochastic Oscillator
    stochastic = StochasticOscillator(
        high=asset_df["high"],
        low=asset_df["low"],
        close=asset_df["close"],
        window=14
    )

    asset_df["stoch_k"] = stochastic.stoch()
    asset_df["stoch_d"] = stochastic.stoch_signal()

    # VWAP
    vwap = VolumeWeightedAveragePrice(
        high=asset_df["high"],
        low=asset_df["low"],
        close=asset_df["close"],
        volume=asset_df["volume"],
        window=14
    )

    asset_df["vwap"] = vwap.volume_weighted_average_price()

    indicator_frames.append(asset_df)

final_df = pd.concat(indicator_frames, ignore_index=True)

final_df = final_df.replace([np.inf, -np.inf], np.nan)

final_df.to_csv(OUTPUT_PATH, index=False)

print("\nTechnical indicators calculated successfully.")
print(f"Saved to: {OUTPUT_PATH}")

print("\nNew Indicator Columns Added:")
new_columns = [
    "rsi_14",
    "macd",
    "macd_signal",
    "macd_diff",
    "bb_high",
    "bb_low",
    "ema_20",
    "ema_50",
    "atr_14",
    "stoch_k",
    "stoch_d",
    "vwap"
]

print(new_columns)

print("\nPreview:")
print(final_df[new_columns].tail())