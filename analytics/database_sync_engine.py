import os
import sqlite3
import pandas as pd

DB_PATH = "data/database/market_intelligence.db"

CSV_TABLE_MAP = {
    "data/processed/combined_historical_market_data.csv": "historical_prices",
    "data/processed/market_features.csv": "market_features",
    "data/processed/market_technical_indicators.csv": "technical_indicators",
    "data/processed/market_signals.csv": "signals",
    "data/processed/market_forecasts.csv": "forecasts",
    "data/processed/asset_risk_summary.csv": "asset_risk_summary",
    "data/processed/market_comparison_summary.csv": "market_comparison_summary",
    "data/processed/unified_market_intelligence.csv": "unified_market_intelligence",
    "data/processed/backtest_summary.csv": "backtest_summary",
    "data/processed/optimized_portfolio_weights.csv": "optimized_portfolio_weights",
    "data/processed/portfolio_optimization_summary.csv": "portfolio_optimization_summary",
    "data/processed/correlation_matrix.csv": "correlation_matrix",
    "data/processed/rolling_correlation_summary.csv": "rolling_correlation_summary",
    "data/processed/diversification_insights.csv": "diversification_insights",
    "data/processed/market_regime_summary.csv": "market_regime_summary",
    "data/processed/historical_market_regimes.csv": "historical_market_regimes"
}

os.makedirs("data/database", exist_ok=True)

conn = sqlite3.connect(DB_PATH)

for csv_path, table_name in CSV_TABLE_MAP.items():
    if os.path.exists(csv_path):
        print(f"Syncing {csv_path} → {table_name}")

        df = pd.read_csv(csv_path)

        df.to_sql(
            table_name,
            conn,
            if_exists="replace",
            index=False
        )

        print(f"Saved table: {table_name} | Rows: {len(df)}")
    else:
        print(f"Missing file, skipped: {csv_path}")

conn.close()

print("\nDatabase sync completed successfully.")
print(f"Database saved at: {DB_PATH}")