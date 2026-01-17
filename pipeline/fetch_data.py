import yfinance as yf
import pandas as pd
import os

DATA_PATH = "data/btc_prices.csv"

def fetch_data():
    """
    Fetches daily BTC-USD data from yfinance and ensures 'Date' is the index.
    Saves to data/btc_prices.csv.
    """
    print("Fetching BTC-USD data...")
    # Fetch max history to ensure we have enough data for rolling windows
    df = yf.download("BTC-USD", interval="1d", period="max", progress=False)
    
    # yfinance returns MultiIndex columns in recent versions, specific check might be needed
    # but usually for a single ticker it's fine or we flatten it.
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    
    # Ensure Date is index and naive UTC (if timezone aware)
    # Spec requires UTC. yfinance returns tz-aware (usually UTC or NYC).
    # We standardise to UTC and remove tz info to keep it simple but strictly UTC-based.
    if df.index.tz is not None:
        df.index = df.index.tz_convert('UTC').tz_localize(None)
    
    # Reset index to make Date a column
    df.reset_index(inplace=True)
    
    # Ensure we have data
    if df.empty:
        raise RuntimeError("yfinance returned empty data. Stopping pipeline.")

    # Keep Date as YYYY-MM-DD string for storage/consistency
    df['Date'] = pd.to_datetime(df['Date']).dt.strftime('%Y-%m-%d')
    
    # Select only necessary columns
    needed_cols = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
    
    # Validate columns exist
    missing_cols = [c for c in needed_cols if c not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing columns in fetched data: {missing_cols}")

    df = df[needed_cols]
    
    # Save
    os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
    df.to_csv(DATA_PATH, index=False)
    print(f"Data saved to {DATA_PATH}. Rows: {len(df)}")

if __name__ == "__main__":
    fetch_data()
