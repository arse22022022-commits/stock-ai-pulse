
import numpy as np
import pandas as pd
import yfinance as yf
from hmmlearn import hmm
import time

def train_and_predict(data, train_on_full=True):
    # Prepare data
    returns = np.log(data / data.shift(1)).dropna().values.reshape(-1, 1)
    
    model = hmm.GaussianHMM(n_components=3, covariance_type="full", n_iter=1000, random_state=42)
    
    try:
        if train_on_full:
            model.fit(returns)
        else:
            # Train on all EXCEPT the last point
            model.fit(returns[:-1])
            
        # Predict on ALL
        states = model.predict(returns)
        return states[-1]
    except Exception as e:
        print(f"Error: {e}")
        return -1

ticker = "LDO.MI"
print(f"--- REAL DATA STABILITY TEST: {ticker} ---")

# Fetch data 3 times with small delay
for i in range(3):
    print(f"\nAttempt {i+1}: Fetching data...")
    df = yf.Ticker(ticker).history(period="1y")
    close_prices = df['Close']
    
    print(f"Last 2 prices: {close_prices.iloc[-2]:.4f} -> {close_prices.iloc[-1]:.4f}")
    
    # Method A
    state_a = train_and_predict(close_prices, train_on_full=True)
    print(f"Method A (Train Full): State {state_a}")
    
    # Method B
    state_b = train_and_predict(close_prices, train_on_full=False)
    print(f"Method B (Train Closed): State {state_b}")
    
    # Simulate a small price change on the last candle
    perturbed_prices = close_prices.copy()
    perturbed_prices.iloc[-1] = perturbed_prices.iloc[-1] * 1.002 # +0.2%
    
    state_a_p = train_and_predict(perturbed_prices, train_on_full=True)
    print(f"Method A (Perturbed +0.2%): State {state_a_p}")

    state_b_p = train_and_predict(perturbed_prices, train_on_full=False)
    print(f"Method B (Perturbed +0.2%): State {state_b_p}")
    
    time.sleep(2)
