import pandas as pd
from datetime import datetime, timedelta
import os
from pipeline.train import train_baseline_model

DATA_PATH = "data/btc_prices.csv"
PREDICTIONS_PATH = "data/predictions.csv"
MODEL_NAME = "linear_baseline"

def run_prediction(as_of_date=None, mode='live'):
    """
    Runs prediction. 
    If as_of_date is provided (YYYY-MM-DD), it simulates running on that day 
    (using data up to that day) to predict as_of_date + 1.
    If as_of_date is None, uses today (live mode).
    
    mode: 'live' or 'backtest'
    """
    print(f"Running prediction pipeline for model: {MODEL_NAME}, Mode: {mode}")
    
    # Load Data
    if not os.path.exists(DATA_PATH):
        print("Data file not found. Run fetch_data first.")
        return
        
    df = pd.read_csv(DATA_PATH)
    df['Date'] = pd.to_datetime(df['Date'])
    
    # Determine the "current" date for the simulation
    if as_of_date:
        current_date_ts = pd.to_datetime(as_of_date)
        # Filter data available UP TO this date
        df_train = df[df['Date'] <= current_date_ts].copy()
    else:
        # Live mode: use all data available
        df_train = df.copy()
        current_date_ts = df['Date'].iloc[-1] # Assuming last row is "today"
        
    if df_train.empty:
        print("No data available for training.")
        return

    # Train
    model = train_baseline_model(df_train)
    
    # Predict
    try:
        predicted_price = model.predict_tomorrow(df_train)
    except ValueError as e:
        print(f"Prediction failed: {e}")
        return

    # Target Date is Current Date + 1 Day
    target_date_ts = current_date_ts + timedelta(days=1)
    target_date_str = target_date_ts.strftime('%Y-%m-%d')
    
    # Generate timestamp
    # In backtest mode, we simulate the created_at time to be the training date + some time
    if mode == 'backtest':
        date_generated = current_date_ts.strftime('%Y-%m-%d 00:05:00')
    else:
        date_generated = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    
    record = {
        'date_generated': date_generated,
        'target_date': target_date_str,
        'model_name': MODEL_NAME,
        'predicted_close': round(predicted_price, 2),
        'actual_close': None, 
        'abs_error': None,
        'pct_error': None
    }
    
    # Save / Idempotency Check
    save_prediction(record)

def save_prediction(record):
    """
    Saves prediction with strict idempotency check.
    """
    if not os.path.exists(PREDICTIONS_PATH):
        predictions_df = pd.DataFrame(columns=['date_generated', 'target_date', 'model_name', 'predicted_close', 'actual_close', 'abs_error', 'pct_error'])
    else:
        predictions_df = pd.read_csv(PREDICTIONS_PATH)
        
    # Idempotency Check: Unique (model_name, target_date)
    # We ignore 'mode' in uniqueness because a prediction is a prediction.
    # If we already have a prediction for this target date by this model, we SKIP.
    existing = predictions_df[
        (predictions_df['target_date'] == record['target_date']) & 
        (predictions_df['model_name'] == record['model_name'])
    ]
    
    if not existing.empty:
        print(f"Prediction for {record['target_date']} by {record['model_name']} already exists. Skipping.")
        return

    # Add new record
    new_row_df = pd.DataFrame([record])
    predictions_df = pd.concat([predictions_df, new_row_df], ignore_index=True)
    
    predictions_df.to_csv(PREDICTIONS_PATH, index=False)
    print(f"Prediction for {record['target_date']}: ${record['predicted_close']:.2f} saved.")

if __name__ == "__main__":
    run_prediction()
