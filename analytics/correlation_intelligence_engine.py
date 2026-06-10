import os
import pandas as pd
import numpy as np

INPUT_PATH = "data/processed/market_features.csv"

CORR_OUTPUT = "data/processed/correlation_matrix.csv"
ROLLING_OUTPUT = "data/processed/rolling_correlation_summary.csv"
INSIGHTS_OUTPUT = "data/processed/diversification_insights.csv"

os.makedirs("data/processed", exist_ok=True)

print("Loading market features...")
df = pd.read_csv(INPUT_PATH)

df["timestamp"] = pd.to_datetime(df["timestamp"])

# Use returns
returns_df = df.pivot_table(
    index="timestamp",
    columns="asset",
    values="daily_return"
)

returns_df = returns_df.sort_index().fillna(0)

# Correlation matrix
corr_matrix = returns_df.corr()

corr_matrix.to_csv(CORR_OUTPUT)

print("\nCorrelation Matrix:")
print(corr_matrix)

# Rolling correlation analysis
rolling_results = []

window = 30

assets = returns_df.columns.tolist()

for i in range(len(assets)):
    for j in range(i + 1, len(assets)):

        asset_1 = assets[i]
        asset_2 = assets[j]

        rolling_corr = (
            returns_df[asset_1]
            .rolling(window)
            .corr(returns_df[asset_2])
        )

        avg_corr = rolling_corr.mean()

        if pd.isna(avg_corr):
            continue

        # Relationship classification
        if avg_corr >= 0.70:
            relationship = "Strong Positive Correlation"
        elif avg_corr >= 0.40:
            relationship = "Moderate Positive Correlation"
        elif avg_corr <= -0.40:
            relationship = "Negative Correlation"
        else:
            relationship = "Weak Correlation"

        diversification_score = 1 - abs(avg_corr)

        rolling_results.append({
            "asset_1": asset_1,
            "asset_2": asset_2,
            "average_rolling_correlation": avg_corr,
            "relationship": relationship,
            "diversification_score": diversification_score
        })

rolling_df = pd.DataFrame(rolling_results)

rolling_df = rolling_df.sort_values(
    by="average_rolling_correlation",
    ascending=False
)

rolling_df.to_csv(ROLLING_OUTPUT, index=False)

# Diversification insights
insights = []

for _, row in rolling_df.iterrows():

    insight = ""

    if row["relationship"] == "Strong Positive Correlation":
        insight = (
            f"{row['asset_1']} and {row['asset_2']} move very similarly. "
            "Holding both may reduce diversification benefits."
        )

    elif row["relationship"] == "Moderate Positive Correlation":
        insight = (
            f"{row['asset_1']} and {row['asset_2']} show moderate co-movement."
        )

    elif row["relationship"] == "Negative Correlation":
        insight = (
            f"{row['asset_1']} and {row['asset_2']} may provide diversification benefits."
        )

    else:
        insight = (
            f"{row['asset_1']} and {row['asset_2']} show weak relationship."
        )

    insights.append({
        "asset_1": row["asset_1"],
        "asset_2": row["asset_2"],
        "relationship": row["relationship"],
        "diversification_score": row["diversification_score"],
        "insight": insight
    })

insights_df = pd.DataFrame(insights)

insights_df.to_csv(INSIGHTS_OUTPUT, index=False)

print("\nRolling Correlation Summary:")
print(rolling_df.head(15))

print("\nDiversification Insights:")
print(insights_df.head(15))

print("\nFiles Saved:")
print(CORR_OUTPUT)
print(ROLLING_OUTPUT)
print(INSIGHTS_OUTPUT)
