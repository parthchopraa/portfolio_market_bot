import subprocess
import time
from datetime import datetime

REFRESH_INTERVAL_SECONDS = 300  # 5 minutes

SCRIPTS = [
    "analytics/technical_indicators_engine.py",
    "analytics/signal_generation_engine.py",
    "analytics/forecasting_engine.py",
    "analytics/market_comparison_engine.py",
    "analytics/portfolio_optimization_engine.py",
    "analytics/correlation_intelligence_engine.py",
    "analytics/market_regime_detection_engine.py",
    "analytics/unified_market_intelligence.py",
    "analytics/database_sync_engine.py"
]

def run_script(script_path):
    print(f"\nRunning: {script_path}")
    result = subprocess.run(
        ["python", script_path],
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        print(f"Completed: {script_path}")
    else:
        print(f"Error in {script_path}")
        print(result.stderr)

while True:
    print("\n======================================")
    print("Auto recalculation started:", datetime.now())
    print("======================================")

    for script in SCRIPTS:
        run_script(script)

    print("\nAuto recalculation completed:", datetime.now())
    print(f"Waiting {REFRESH_INTERVAL_SECONDS} seconds...")

    time.sleep(REFRESH_INTERVAL_SECONDS)