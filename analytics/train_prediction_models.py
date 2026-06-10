import os
import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor

INPUT_PATH = "data/processed/market_features.csv"

os.makedirs("data/processed", exist_ok=True)

print("Loading feature dataset...")
df = pd.read_csv(INPUT_PATH)

# Features
FEATURE_COLUMNS = [
    "daily_return",
    "log_return",
    "ma_7",
    "ma_30",
    "volatility_7",
    "volatility_30",
    "volume_change",
    "momentum_7",
    "momentum_30",
    "drawdown"
]

TARGET_COLUMN = "next_day_return"

# Keep needed columns
model_df = df[FEATURE_COLUMNS + [TARGET_COLUMN]].copy()

# Clean NaNs
model_df = model_df.dropna()

X = model_df[FEATURE_COLUMNS]
y = model_df[TARGET_COLUMN]

# Split
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

print(f"\nTraining rows: {len(X_train)}")
print(f"Testing rows: {len(X_test)}")

# -----------------------------
# Linear Regression
# -----------------------------
print("\nTraining Linear Regression...")

lr_model = LinearRegression()
lr_model.fit(X_train, y_train)

lr_predictions = lr_model.predict(X_test)

# Metrics
lr_mae = mean_absolute_error(y_test, lr_predictions)
lr_rmse = np.sqrt(mean_squared_error(y_test, lr_predictions))
lr_r2 = r2_score(y_test, lr_predictions)

print("\nLinear Regression Results")
print("----------------------------")
print(f"MAE: {lr_mae}")
print(f"RMSE: {lr_rmse}")
print(f"R²: {lr_r2}")

# -----------------------------
# Random Forest
# -----------------------------
print("\nTraining Random Forest...")

rf_model = RandomForestRegressor(
    n_estimators=100,
    random_state=42,
    n_jobs=-1
)

rf_model.fit(X_train, y_train)

rf_predictions = rf_model.predict(X_test)

# Metrics
rf_mae = mean_absolute_error(y_test, rf_predictions)
rf_rmse = np.sqrt(mean_squared_error(y_test, rf_predictions))
rf_r2 = r2_score(y_test, rf_predictions)

print("\nRandom Forest Results")
print("----------------------------")
print(f"MAE: {rf_mae}")
print(f"RMSE: {rf_rmse}")
print(f"R²: {rf_r2}")

# -----------------------------
# Feature Importance
# -----------------------------
feature_importance = pd.DataFrame({
    "feature": FEATURE_COLUMNS,
    "importance": rf_model.feature_importances_
})

feature_importance = feature_importance.sort_values(
    by="importance",
    ascending=False
)

print("\nFeature Importance")
print("----------------------------")
print(feature_importance)

# Save feature importance
feature_importance.to_csv(
    "data/processed/feature_importance.csv",
    index=False
)

print("\nFeature importance saved.")