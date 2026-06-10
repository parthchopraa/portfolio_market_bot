import os
import pandas as pd
import numpy as np

INPUT_PATH = "data/processed/market_technical_indicators.csv"
OUTPUT_PATH = "data/processed/backtest_results.csv"
SUMMARY_PATH = "data/processed/backtest_summary.csv"

os.makedirs("data/processed", exist_ok=True)

print("Loading technical indicators...")
df = pd.read_csv(INPUT_PATH)

df["timestamp"] = pd.to_datetime(df["timestamp"])
df = df.sort_values(["asset", "timestamp"]).reset_index(drop=True)

all_backtests = []
summaries = []

for asset, asset_df in df.groupby("asset"):
    print(f"Backtesting {asset}...")

    asset_df = asset_df.sort_values("timestamp").copy()

    # Clean required fields
    asset_df = asset_df.dropna(subset=[
        "close",
        "daily_return",
        "rsi_14",
        "macd",
        "macd_signal",
        "ema_20",
        "ema_50",
        "volatility_30"
    ])

    if len(asset_df) < 100:
        continue

    # Strategy signal
    asset_df["strategy_signal"] = 0

    buy_condition = (
        (asset_df["ema_20"] > asset_df["ema_50"]) &
        (asset_df["macd"] > asset_df["macd_signal"]) &
        (asset_df["rsi_14"] < 70)
    )

    sell_condition = (
        (asset_df["ema_20"] < asset_df["ema_50"]) |
        (asset_df["macd"] < asset_df["macd_signal"]) |
        (asset_df["rsi_14"] > 75)
    )

    asset_df.loc[buy_condition, "strategy_signal"] = 1
    asset_df.loc[sell_condition, "strategy_signal"] = 0

    # Position uses previous day signal to avoid lookahead bias
    asset_df["position"] = asset_df["strategy_signal"].shift(1).fillna(0)

    # Strategy returns
    asset_df["strategy_return"] = asset_df["position"] * asset_df["daily_return"]

    # Buy and hold return
    asset_df["buy_hold_return"] = asset_df["daily_return"]

    # Cumulative returns
    asset_df["strategy_cumulative"] = (1 + asset_df["strategy_return"]).cumprod()
    asset_df["buy_hold_cumulative"] = (1 + asset_df["buy_hold_return"]).cumprod()

    # Drawdown
    asset_df["strategy_peak"] = asset_df["strategy_cumulative"].cummax()
    asset_df["strategy_drawdown"] = (
        asset_df["strategy_cumulative"] - asset_df["strategy_peak"]
    ) / asset_df["strategy_peak"]

    # Metrics
    strategy_total_return = asset_df["strategy_cumulative"].iloc[-1] - 1
    buy_hold_total_return = asset_df["buy_hold_cumulative"].iloc[-1] - 1

    strategy_volatility = asset_df["strategy_return"].std() * np.sqrt(252)

    strategy_sharpe = (
        (asset_df["strategy_return"].mean() / asset_df["strategy_return"].std()) * np.sqrt(252)
        if asset_df["strategy_return"].std() != 0
        else np.nan
    )

    max_drawdown = asset_df["strategy_drawdown"].min()

    trades = asset_df["position"].diff().abs().sum()

    win_rate = (
        (asset_df["strategy_return"] > 0).sum()
        / (asset_df["strategy_return"] != 0).sum()
        if (asset_df["strategy_return"] != 0).sum() > 0
        else np.nan
    )

    summaries.append({
        "asset": asset,
        "asset_type": asset_df["asset_type"].iloc[0],
        "strategy_total_return": strategy_total_return,
        "buy_hold_total_return": buy_hold_total_return,
        "strategy_volatility": strategy_volatility,
        "strategy_sharpe": strategy_sharpe,
        "max_drawdown": max_drawdown,
        "number_of_trades": trades,
        "win_rate": win_rate
    })

    all_backtests.append(asset_df[[
        "timestamp",
        "asset",
        "asset_type",
        "close",
        "strategy_signal",
        "position",
        "daily_return",
        "strategy_return",
        "buy_hold_return",
        "strategy_cumulative",
        "buy_hold_cumulative",
        "strategy_drawdown"
    ]])

backtest_df = pd.concat(all_backtests, ignore_index=True)
summary_df = pd.DataFrame(summaries)

backtest_df.to_csv(OUTPUT_PATH, index=False)
summary_df.to_csv(SUMMARY_PATH, index=False)

print("\nBacktesting completed.")
print(f"Saved detailed results to: {OUTPUT_PATH}")
print(f"Saved summary to: {SUMMARY_PATH}")

print("\nBacktest Summary:")
print(summary_df.sort_values("strategy_sharpe", ascending=False))