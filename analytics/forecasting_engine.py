import os
import warnings
import pandas as pd
import numpy as np

from statsmodels.tsa.arima.model import ARIMA
from sklearn.metrics import mean_absolute_error, mean_squared_error

warnings.filterwarnings("ignore")

INPUT_PATH = "data/processed/market_technical_indicators.csv"
OUTPUT_PATH = "data/processed/market_forecasts.csv"

os.makedirs("data/processed", exist_ok=True)

print("Loading market data...")
df = pd.read_csv(INPUT_PATH)

df["timestamp"] = pd.to_datetime(df["timestamp"])
df = df.sort_values(["asset", "timestamp"]).reset_index(drop=True)

forecast_results = []

for asset, asset_df in df.groupby("asset"):

    print(f"\nForecasting {asset}...")

    asset_df = asset_df.sort_values("timestamp").copy()
    asset_df = asset_df.dropna(subset=["close"])

    # Use latest 500 records for speed and relevance
    asset_df = asset_df.tail(500)

    prices = asset_df["close"]

    if len(prices) < 100:
        print(f"Skipping {asset}: not enough data")
        continue

    train_size = int(len(prices) * 0.8)

    train = prices.iloc[:train_size]
    test = prices.iloc[train_size:]

    try:
        model = ARIMA(train, order=(5, 1, 0))
        fitted_model = model.fit()

        predictions = fitted_model.forecast(steps=len(test))

        mae = mean_absolute_error(test, predictions)
        rmse = np.sqrt(mean_squared_error(test, predictions))

        # Forecast next day
        final_model = ARIMA(prices, order=(5, 1, 0))
        final_fitted = final_model.fit()

        next_forecast = final_fitted.forecast(steps=1).iloc[0]

        latest_close = prices.iloc[-1]

        predicted_return = (next_forecast - latest_close) / latest_close

        if predicted_return > 0.01:
            forecast_direction = "UP"
        elif predicted_return < -0.01:
            forecast_direction = "DOWN"
        else:
            forecast_direction = "SIDEWAYS"

        forecast_results.append({
            "asset": asset,
            "asset_type": asset_df["asset_type"].iloc[-1],
            "latest_date": asset_df["timestamp"].iloc[-1],
            "latest_close": latest_close,
            "next_forecast_close": next_forecast,
            "predicted_return": predicted_return,
            "forecast_direction": forecast_direction,
            "model": "ARIMA(5,1,0)",
            "mae": mae,
            "rmse": rmse
        })

        print(f"{asset}: latest={latest_close:.2f}, forecast={next_forecast:.2f}, direction={forecast_direction}")

    except Exception as e:
        print(f"Forecasting failed for {asset}: {e}")

forecast_df = pd.DataFrame(forecast_results)

forecast_df.to_csv(OUTPUT_PATH, index=False)

print("\nForecasting completed.")
print(f"Saved to: {OUTPUT_PATH}")

print("\nForecast Results:")
print(forecast_df[[
    "asset",
    "asset_type",
    "latest_close",
    "next_forecast_close",
    "predicted_return",
    "forecast_direction",
    "rmse"
]])