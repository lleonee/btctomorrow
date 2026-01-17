1. System Architecture Overview

Architecture Type

Offline ML + static frontend

Daily batch prediction pipeline

Components

GitHub Actions → data, training, prediction

Python ML pipeline

CSV/JSON storage in repo

GitHub Pages → visualization only

No backend server. No database. No APIs.

2. Prediction Definition (Locked)

Asset: Bitcoin (BTC-USD)

Source: yfinance

Target: Next UTC daily close price

Prediction time: Once per day, shortly after UTC close

Frequency: Daily

3. ML Model Requirements (Baseline Phase)
3.1 Model Philosophy

Baseline, interpretable, fast

Designed to be replaceable

One model = one file

3.2 Baseline Model (Phase 1 – Required)

Algorithm: Linear Regression

Library: scikit-learn

Training style: Retrain daily on full history

3.3 Features (Minimal, Deterministic)

From daily OHLCV:

Close price (lagged)

Daily return

Rolling means:

3-day MA

7-day MA

14-day MA

Rolling volatility (7-day std)

Target:

Next day close price

4. Future Models (Phase 2 – Not Implemented Yet)

Must be scaffolded, not built

ARIMA

Prophet

LSTM

Hybrid / ensemble

Rule

Each model:

Separate Python file

Same input/output interface

Same prediction storage format

5. Data Pipeline Specification
5.1 Data Source

yfinance.download("BTC-USD", interval="1d")

5.2 Update Frequency

Daily via GitHub Actions cron

5.3 Storage (Authoritative)

CSV files committed to repo

Required Files

data/btc_prices.csv (raw OHLCV)

data/predictions.csv (append-only)

6. Prediction Tracking Methodology
predictions.csv schema (MANDATORY)
column	description
date_generated	UTC date prediction was made
target_date	Date being predicted
model_name	e.g. "linear_baseline"
predicted_close	Float
actual_close	Float or NaN
abs_error	Float or NaN
pct_error	Float or NaN

Rules

Prediction is written before actual is known

Actual price filled in next day

Errors computed when actual exists

Never overwrite rows

7. GitHub Actions (Execution Engine)
7.1 Trigger

Cron: once per day (UTC)

Manual trigger allowed

7.2 Steps

Checkout repo

Set up Python 3.10

Install dependencies

Run run_pipeline.py

Commit updated CSV + JSON

Push to main

7.3 Environment

GitHub-hosted Ubuntu runner

No secrets required

No external services

8. Frontend (GitHub Pages)
8.1 Stack

Static HTML

CSS

Vanilla JavaScript

Chart.js (or similar)

8.2 Pages Required

Home

Latest prediction

Model name

Target date

History

Table of all predictions

Performance

Line chart: predicted vs actual

Error metrics over time

8.3 Data Loading

Fetch CSV/JSON directly from repo

No backend calls

9. Repository File Structure (STRICT)
/
├── data/
│   ├── btc_prices.csv
│   └── predictions.csv
│
├── models/
│   └── linear_baseline.py
│
├── pipeline/
│   ├── fetch_data.py
│   ├── train.py
│   ├── predict.py
│   └── evaluate.py
│
├── run_pipeline.py
│
├── site/
│   ├── index.html
│   ├── history.html
│   ├── performance.html
│   ├── styles.css
│   └── app.js
│
├── .github/workflows/
│   └── daily_predict.yml
│
├── requirements.txt
└── README.md

10. Technology Stack (Locked)

Python 3.10

yfinance

pandas

numpy

scikit-learn

GitHub Actions

GitHub Pages

11. Validation Checklist (For AI Developer)

⬜ Daily prediction runs automatically

⬜ Tomorrow’s UTC close predicted

⬜ Predictions stored historically (never overwritten)

⬜ Errors computed after actual close

⬜ Site displays latest + historical predictions

⬜ Code structured for future models

⬜ No backend / server dependency