# btctomorrow

Simple offline ML system to predict daily Bitcoin close prices.

## Architecture
- **Data Source**: yfinance (BTC-USD)
- **Model**: Linear Regression (Baseline)
- **Pipeline**: Daily GitHub Actions workflow
- **Storage**: CSV files in `data/`
- **Frontend**: GitHub Pages (Static)

## Setup
```bash
pip install -r requirements.txt
```

## Usage

### Live Mode (Default)
Runs a single prediction for "tomorrow" based on the latest available data. Designed to run daily.
```bash
python run_pipeline.py
# Equivalent to:
python run_pipeline.py --mode live
```

### Backtest Mode
Simulates daily runs over a past date range to generate historical predictions.
```bash
python run_pipeline.py --mode backtest --start-date 2026-01-01
```

## Rules
- **Idempotency**: The system will not overwrite or duplicate a prediction for the same model and target date.
- **Time**: All internal logic uses strict UTC.
- **Fail-Fast**: The pipeline stops immediately if data fetching is incomplete or empty.
