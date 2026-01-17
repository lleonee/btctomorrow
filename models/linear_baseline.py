import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error

class LinearBaselineModel:
    def __init__(self):
        self.model = LinearRegression()
        self.features = ['Close', 'Return', 'MA_3', 'MA_7', 'MA_14', 'Vol_7']
        self.target = 'Target'

    def prepare_features(self, df_raw):
        """
        Generates features and target for training.
        df_raw: DataFrame with Date, Close, etc.
        Returns: DataFrame with features and Target (NaN for average last row).
        """
        df = df_raw.copy()
        
        # Sort by date
        df.sort_values(by='Date', inplace=True)
        
        # 1. Base Features
        # "Close (lagged)" -> In the context of predicting t+1, 'Close' at t IS the lagged close relative to t+1.
        # So we just use 'Close'.
        
        # Daily Return
        df['Return'] = df['Close'].pct_change()
        
        # Rolling Means
        df['MA_3'] = df['Close'].rolling(window=3).mean()
        df['MA_7'] = df['Close'].rolling(window=7).mean()
        df['MA_14'] = df['Close'].rolling(window=14).mean()
        
        # Rolling Volatility (7-day std)
        df['Vol_7'] = df['Close'].rolling(window=7).std()
        
        # 2. Target: Next day close
        df['Target'] = df['Close'].shift(-1)
        
        return df

    def train(self, df):
        """
        Trains the model on the full dataset (excluding the last row where target is NaN).
        """
        data = self.prepare_features(df)
        
        # Drop rows with NaN in features or target
        train_data = data.dropna(subset=self.features + [self.target])
        
        X = train_data[self.features]
        y = train_data[self.target]
        
        self.model.fit(X, y)
        print(f"Model trained on {len(train_data)} rows.")
        
        # Optional: Print generic in-sample score
        score = self.model.score(X, y)
        print(f"R^2 Score: {score:.4f}")

    def predict_tomorrow(self, df):
        """
        Predicts the Close price for the next day (tomorrow) using the latest available data.
        """
        data = self.prepare_features(df)
        
        # The last row has features for "today" to predict "tomorrow"
        # Target is NaN here, but features should be valid if we have enough history.
        last_row = data.iloc[[-1]] 
        
        # Check if features are NaN (e.g. not enough data for MA_14)
        if last_row[self.features].isnull().values.any():
            raise ValueError("Not enough data to generate features for the last row.")
            
        X_predict = last_row[self.features]
        prediction = self.model.predict(X_predict)[0]
        
        return prediction
