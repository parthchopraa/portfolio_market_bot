import os
import pandas as pd
import numpy as np
from scipy.optimize import minimize

INPUT_PATH = "data/processed/market_features.csv"

OUTPUT_WEIGHTS_PATH = "data/processed/optimized_portfolio_weights.csv"
OUTPUT_SUMMARY_PATH = "data/processed/portfolio_optimization_summary.csv"

os.makedirs("data/processed", exist_ok=True)

print("Loading market features...")
df = pd.read_csv(INPUT_PATH)
df["timestamp"] = pd.to_datetime(df["timestamp"])

# Keep only clean return data
df = df.dropna(subset=["daily_return"])

# Asset type mapping
asset_type_map = df.groupby("asset")["asset_type"].first().to_dict()

# Pivot returns
returns_df = df.pivot_table(
    index="timestamp",
    columns="asset",
    values="daily_return"
)

# Align stock/crypto calendars:
# Fill missing returns with 0, meaning no recorded movement/trading that day
returns_df = returns_df.sort_index().fillna(0)

assets = returns_df.columns.tolist()
num_assets = len(assets)

mean_returns = returns_df.mean() * 252
cov_matrix = returns_df.cov() * 252

risk_free_rate = 0.02

def portfolio_performance(weights):
    portfolio_return = np.sum(weights * mean_returns)
    portfolio_volatility = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))

    if portfolio_volatility == 0:
        sharpe_ratio = 0
    else:
        sharpe_ratio = (portfolio_return - risk_free_rate) / portfolio_volatility

    return portfolio_return, portfolio_volatility, sharpe_ratio

def negative_sharpe(weights):
    return -portfolio_performance(weights)[2]

def portfolio_volatility(weights):
    return portfolio_performance(weights)[1]

# Constraints
constraints = [
    {
        "type": "eq",
        "fun": lambda weights: np.sum(weights) - 1
    }
]

# Crypto exposure max 35%
crypto_indices = [
    i for i, asset in enumerate(assets)
    if asset_type_map.get(asset) == "Cryptocurrency"
]

stock_indices = [
    i for i, asset in enumerate(assets)
    if asset_type_map.get(asset) == "Stock"
]

constraints.append({
    "type": "ineq",
    "fun": lambda weights: 0.35 - np.sum(weights[crypto_indices])
})

# Stock exposure max 85%
constraints.append({
    "type": "ineq",
    "fun": lambda weights: 0.85 - np.sum(weights[stock_indices])
})

# At least 15% stocks
constraints.append({
    "type": "ineq",
    "fun": lambda weights: np.sum(weights[stock_indices]) - 0.15
})

# Bounds: max 25% per asset
bounds = tuple((0, 0.25) for _ in range(num_assets))

initial_weights = np.array(num_assets * [1.0 / num_assets])

# Maximum Sharpe Portfolio
max_sharpe_result = minimize(
    negative_sharpe,
    initial_weights,
    method="SLSQP",
    bounds=bounds,
    constraints=constraints
)

max_sharpe_weights = max_sharpe_result.x
max_return, max_volatility, max_sharpe = portfolio_performance(max_sharpe_weights)

# Minimum Volatility Portfolio
min_vol_result = minimize(
    portfolio_volatility,
    initial_weights,
    method="SLSQP",
    bounds=bounds,
    constraints=constraints
)

min_vol_weights = min_vol_result.x
min_return, min_volatility, min_sharpe = portfolio_performance(min_vol_weights)

# Equal Weight Portfolio
equal_weights = initial_weights
eq_return, eq_volatility, eq_sharpe = portfolio_performance(equal_weights)

weights_df = pd.DataFrame({
    "asset": assets,
    "asset_type": [asset_type_map.get(asset) for asset in assets],
    "max_sharpe_weight": max_sharpe_weights,
    "min_volatility_weight": min_vol_weights,
    "equal_weight": equal_weights
})

summary_df = pd.DataFrame([
    {
        "portfolio_type": "Maximum Sharpe Portfolio",
        "expected_annual_return": max_return,
        "annual_volatility": max_volatility,
        "sharpe_ratio": max_sharpe
    },
    {
        "portfolio_type": "Minimum Volatility Portfolio",
        "expected_annual_return": min_return,
        "annual_volatility": min_volatility,
        "sharpe_ratio": min_sharpe
    },
    {
        "portfolio_type": "Equal Weight Portfolio",
        "expected_annual_return": eq_return,
        "annual_volatility": eq_volatility,
        "sharpe_ratio": eq_sharpe
    }
])

weights_df.to_csv(OUTPUT_WEIGHTS_PATH, index=False)
summary_df.to_csv(OUTPUT_SUMMARY_PATH, index=False)

print("\nPortfolio Optimization v2 completed.")
print(f"Assets included: {len(assets)}")
print(f"Weights saved to: {OUTPUT_WEIGHTS_PATH}")
print(f"Summary saved to: {OUTPUT_SUMMARY_PATH}")

print("\nOptimization Summary:")
print(summary_df)

print("\nOptimized Weights:")
print(weights_df.sort_values("max_sharpe_weight", ascending=False))

print("\nCrypto Exposure:")
print(weights_df.loc[weights_df["asset_type"] == "Cryptocurrency", "max_sharpe_weight"].sum())

print("\nStock Exposure:")
print(weights_df.loc[weights_df["asset_type"] == "Stock", "max_sharpe_weight"].sum())