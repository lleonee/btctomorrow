import argparse
from datetime import datetime, timedelta
import pandas as pd
from pipeline.fetch_data import fetch_data
from pipeline.evaluate import evaluate_predictions
from pipeline.predict import run_prediction

def main():
    parser = argparse.ArgumentParser(description="BTC Tomorrow Pipeline")
    parser.add_argument('--mode', choices=['live', 'backtest'], default='live', help="Execution mode")
    parser.add_argument('--start-date', help="Start date for backtest (YYYY-MM-DD)")
    parser.add_argument('--end-date', help="End date for backtest (YYYY-MM-DD), defaults to today")
    
    args = parser.parse_args()
    
    print(f"=== Starting Pipeline (Mode: {args.mode}) ===")
    
    # 1. Update Data (Always needed)
    print("\n--- Step 1: Fetch Data ---")
    fetch_data()
    
    # 2. Evaluate Past Predictions
    print("\n--- Step 2: Evaluate ---")
    evaluate_predictions()
    
    # 3. Predict
    print("\n--- Step 3: Predict ---")
    
    if args.mode == 'live':
        # Single run for "today" to predict "tomorrow"
        run_prediction(mode='live')
        
    elif args.mode == 'backtest':
        if not args.start_date:
            print("Error: --start-date required for backtest.")
            return

        start = pd.to_datetime(args.start_date)
        end = pd.to_datetime(args.end_date) if args.end_date else pd.to_datetime(datetime.utcnow().date())
        
        print(f"Backtesting from {start.date()} to {end.date()}...")
        
        current = start
        while current <= end:
            date_str = current.strftime('%Y-%m-%d')
            print(f"Backtest Day: {date_str}")
            run_prediction(as_of_date=date_str, mode='backtest')
            current += timedelta(days=1)
            
            # Re-evaluate after each prediction to fill potential actuals if we were looping strictly
            # But evaluate_predictions() checks actuals from the FULL price data we just fetched.
            # So running it once at start is mostly fine, BUT for a backtest where we want to generate
            # the history file as if we ran it daily, we might want to fill actuals for the prediction 
            # we just made? No, we can't fill actual for T+1 when we are at T.
            # We can only fill actuals for T-1.
            # Since backtest generates row for T+1, we can't fill it yet.
            # We can run evaluate_predictions at the very end of backtest loop?
            # Or run it blindly inside loop.
            pass
        
        # Final pass to fill actuals for all the predictions we just generated (except the very last one)
        print("\n--- Final Evaluation Pass ---")
        evaluate_predictions()

    print("\n=== Pipeline Complete ===")

if __name__ == "__main__":
    main()
