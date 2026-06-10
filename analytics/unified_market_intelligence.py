import os
import pandas as pd
import numpy as np

SIGNALS_PATH = "data/processed/market_signals.csv"
FORECASTS_PATH = "data/processed/market_forecasts.csv"
RISK_PATH = "data/processed/asset_risk_summary.csv"
REGIME_PATH = "data/processed/market_regime_summary.csv"
BACKTEST_PATH = "data/processed/backtest_summary.csv"
CORRELATION_PATH = "data/processed/rolling_correlation_summary.csv"

OUTPUT_PATH = "data/processed/unified_market_intelligence.csv"

os.makedirs("data/processed", exist_ok=True)

signals_df = pd.read_csv(SIGNALS_PATH)
forecasts_df = pd.read_csv(FORECASTS_PATH)
risk_df = pd.read_csv(RISK_PATH)
regime_df = pd.read_csv(REGIME_PATH)
backtest_df = pd.read_csv(BACKTEST_PATH)
corr_df = pd.read_csv(CORRELATION_PATH)

# Correlation risk per asset
correlation_rows = []

for asset in signals_df["asset"].unique():
    related = corr_df[
        (corr_df["asset_1"] == asset) | (corr_df["asset_2"] == asset)
    ]

    if len(related) == 0:
        avg_corr = np.nan
    else:
        avg_corr = related["average_rolling_correlation"].abs().mean()

    if pd.isna(avg_corr):
        corr_risk = "Unknown"
        corr_penalty = 0
    elif avg_corr >= 0.65:
        corr_risk = "High Correlation Risk"
        corr_penalty = 1
    elif avg_corr >= 0.40:
        corr_risk = "Moderate Correlation Risk"
        corr_penalty = 0.5
    else:
        corr_risk = "Low Correlation Risk"
        corr_penalty = -0.5

    correlation_rows.append({
        "asset": asset,
        "average_abs_correlation": avg_corr,
        "correlation_risk": corr_risk,
        "correlation_penalty": corr_penalty
    })

correlation_risk_df = pd.DataFrame(correlation_rows)

df = signals_df.merge(
    forecasts_df[["asset", "predicted_return", "forecast_direction", "rmse"]],
    on="asset",
    how="left"
)

df = df.merge(
    risk_df[[
        "asset",
        "annual_return",
        "annual_volatility",
        "sharpe_ratio",
        "max_drawdown",
        "risk_score",
        "risk_category",
        "market_stance"
    ]],
    on="asset",
    how="left"
)

df = df.merge(
    regime_df[["asset", "market_regime", "rolling_return_30", "rolling_volatility_30"]],
    on="asset",
    how="left"
)

df = df.merge(
    backtest_df[[
        "asset",
        "strategy_total_return",
        "buy_hold_total_return",
        "strategy_sharpe",
        "max_drawdown",
        "win_rate"
    ]],
    on="asset",
    how="left",
    suffixes=("", "_backtest")
)

df = df.merge(
    correlation_risk_df,
    on="asset",
    how="left"
)

final_rows = []

for _, row in df.iterrows():
    evidence_score = 0
    risk_penalty = 0
    reliability_score = 0
    reasons = []

    signal_score = row.get("signal_score", 0)
    risk_score = row.get("risk_score", np.nan)
    sharpe = row.get("sharpe_ratio", np.nan)
    forecast_direction = row.get("forecast_direction", "SIDEWAYS")
    predicted_return = row.get("predicted_return", 0)
    market_stance = row.get("market_stance", "")
    market_regime = row.get("market_regime", "")
    strategy_sharpe = row.get("strategy_sharpe", np.nan)
    win_rate = row.get("win_rate", np.nan)
    correlation_penalty = row.get("correlation_penalty", 0)

    # Technical signal
    if signal_score >= 6:
        evidence_score += 3
        reasons.append("Strong technical signal")
    elif signal_score >= 4:
        evidence_score += 2
        reasons.append("Positive technical signal")
    elif signal_score >= 2:
        evidence_score += 1
        reasons.append("Mild positive technical signal")
    elif signal_score <= -6:
        evidence_score -= 3
        reasons.append("Strong negative technical signal")
    elif signal_score <= -4:
        evidence_score -= 2
        reasons.append("Negative technical signal")
    elif signal_score <= -2:
        evidence_score -= 1
        reasons.append("Mild negative technical signal")
    else:
        reasons.append("Technical signal is neutral")

    # Forecast
    if forecast_direction == "UP" and predicted_return > 0.005:
        evidence_score += 2
        reasons.append("Forecast supports upside")
    elif forecast_direction == "DOWN" and predicted_return < -0.005:
        evidence_score -= 2
        reasons.append("Forecast supports downside")
    else:
        reasons.append("Forecast is neutral/sideways")

    # Risk-adjusted performance
    if pd.notna(sharpe):
        if sharpe > 1:
            evidence_score += 1
            reasons.append("Strong historical risk-adjusted return")
        elif sharpe > 0.5:
            evidence_score += 0.5
            reasons.append("Acceptable risk-adjusted return")
        elif sharpe < 0:
            evidence_score -= 1
            reasons.append("Weak risk-adjusted return")

    # Market stance
    if market_stance == "Positive Trend":
        evidence_score += 1
        reasons.append("Positive market stance")
    elif market_stance == "Weak Trend":
        evidence_score -= 1
        reasons.append("Weak market stance")

    # Market regime
    if market_regime == "Bullish Regime":
        evidence_score += 1
        reasons.append("Bullish market regime")
    elif market_regime == "Bearish Regime":
        evidence_score -= 2
        reasons.append("Bearish market regime")
    elif market_regime == "High Volatility Regime":
        risk_penalty += 1.5
        reasons.append("High volatility regime increases risk")
    elif market_regime == "Stable / Sideways Regime":
        evidence_score += 0.5
        reasons.append("Stable/sideways regime")

    # Backtest reliability
    if pd.notna(strategy_sharpe):
        if strategy_sharpe > 1:
            reliability_score += 1.5
            reasons.append("Backtest shows strong strategy Sharpe")
        elif strategy_sharpe > 0.5:
            reliability_score += 1
            reasons.append("Backtest shows acceptable strategy Sharpe")
        elif strategy_sharpe < 0:
            reliability_score -= 1
            reasons.append("Backtest performance is weak")

    if pd.notna(win_rate):
        if win_rate > 0.55:
            reliability_score += 1
            reasons.append("Backtest win rate is strong")
        elif win_rate > 0.50:
            reliability_score += 0.5
            reasons.append("Backtest win rate is acceptable")
        else:
            reliability_score -= 0.5
            reasons.append("Backtest win rate is weak")

    # Risk score penalty
    if pd.notna(risk_score):
        if risk_score >= 9:
            risk_penalty += 2
            reasons.append("Very high asset risk")
        elif risk_score >= 7:
            risk_penalty += 1.5
            reasons.append("High asset risk")
        elif risk_score <= 3:
            risk_penalty -= 0.5
            reasons.append("Low asset risk")

    # Correlation penalty
    if pd.notna(correlation_penalty):
        risk_penalty += correlation_penalty
        if correlation_penalty > 0:
            reasons.append("Correlation risk reduces diversification benefit")
        elif correlation_penalty < 0:
            reasons.append("Low correlation improves diversification benefit")

    final_score = evidence_score + reliability_score - risk_penalty

    # Final recommendation
    if final_score >= 6 and risk_score <= 4:
        recommendation = "CONSERVATIVE STRONG BUY"
    elif final_score >= 5 and risk_score <= 6:
        recommendation = "MODERATE STRONG BUY"
    elif final_score >= 4 and risk_score >= 7:
        recommendation = "SPECULATIVE BUY"
    elif final_score >= 3:
        recommendation = "CAUTIOUS BUY"
    elif final_score <= -3:
        recommendation = "SELL / AVOID"
    elif risk_score >= 8:
        recommendation = "HIGH-RISK HOLD"
    else:
        recommendation = "NEUTRAL HOLD"

    confidence = min(abs(final_score) / 8, 1.0)

    if confidence >= 0.75:
        confidence_level = "High"
    elif confidence >= 0.40:
        confidence_level = "Medium"
    else:
        confidence_level = "Low"

    final_rows.append({
        "asset": row["asset"],
        "asset_type": row["asset_type"],
        "close": row["close"],
        "technical_signal": row["signal"],
        "forecast_direction": forecast_direction,
        "market_regime": market_regime,
        "risk_score": risk_score,
        "risk_category": row.get("risk_category"),
        "strategy_sharpe": strategy_sharpe,
        "win_rate": win_rate,
        "correlation_risk": row.get("correlation_risk"),
        "evidence_score": round(evidence_score, 2),
        "reliability_score": round(reliability_score, 2),
        "risk_penalty": round(risk_penalty, 2),
        "final_score": round(final_score, 2),
        "final_recommendation": recommendation,
        "confidence": round(confidence, 2),
        "confidence_level": confidence_level,
        "reason": "; ".join(reasons)
    })

final_df = pd.DataFrame(final_rows)

final_df = final_df.sort_values(
    by=["final_score", "confidence"],
    ascending=False
)

final_df.to_csv(OUTPUT_PATH, index=False)

print("\nUnified Market Intelligence v3 generated.")
print(f"Saved to: {OUTPUT_PATH}")

print("\nFinal Recommendations:")
print(final_df[[
    "asset",
    "asset_type",
    "final_score",
    "final_recommendation",
    "confidence_level",
    "risk_category",
    "market_regime",
    "correlation_risk"
]])