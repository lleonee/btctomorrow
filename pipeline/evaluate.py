import pandas as pd
import os

PREDICTIONS_PATH = "data/predictions.csv"
PRICES_PATH = "data/btc_prices.csv"

def evaluate_predictions():
    """
    Updates 'predictions.csv' with actual values and error metrics
    for past predictions that are missing outcomes.
    """
    if not os.path.exists(PREDICTIONS_PATH) or not os.path.exists(PRICES_PATH):
        print("Files missing for evaluation.")
        return

    preds_df = pd.read_csv(PREDICTIONS_PATH)
    prices_df = pd.read_csv(PRICES_PATH)
    
    # Ensure dates are strings for matching
    # preds_df['target_date'] is YYYY-MM-DD
    # prices_df['Date'] is YYYY-MM-DD
    
    # Convert 'Date' in prices to string YYYY-MM-DD if not already
    prices_df['Date'] = pd.to_datetime(prices_df['Date']).dt.strftime('%Y-%m-%d')
    price_map = dict(zip(prices_df['Date'], prices_df['Close']))
    
    updated = False
    
    for index, row in preds_df.iterrows():
        # Only check incomplete rows
        if pd.isna(row['actual_close']):
            target_date = row['target_date']
            
            if target_date in price_map:
                actual = price_map[target_date]
                predicted = row['predicted_close']
                
                # Calculate errors
                abs_error = abs(actual - predicted)
                pct_error = (abs_error / actual) * 100
                
                # Update row
                preds_df.at[index, 'actual_close'] = actual
                preds_df.at[index, 'abs_error'] = abs_error
                preds_df.at[index, 'pct_error'] = pct_error
                updated = True
                print(f"Evaluated prediction for {target_date}: Actual={actual:.2f}, Error={pct_error:.2f}%")
    
    if updated:
        preds_df.to_csv(PREDICTIONS_PATH, index=False)
        print("Evaluations saved.")
    else:
        print("No new evaluations to make.")

if __name__ == "__main__":
    evaluate_predictions()
