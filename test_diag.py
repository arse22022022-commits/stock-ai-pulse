import yfinance as yf
import pandas as pd
import numpy as np
import time
from hmmlearn import hmm

ticker = 'LDO.MI'
print(f"Fetching {ticker}")
data = yf.Ticker(ticker).history(period="1y", auto_adjust=True)
print(f"Loaded {len(data)} items")

price_col = 'Close'
data['Returns'] = np.log(data[price_col] / data[price_col].shift(1))
data['Diff_Returns'] = data['Returns'].diff()
data.dropna(inplace=True)

print("Starting HMM Training...")
start = time.time()
returns_data = data[['Returns']].values
model_ret = hmm.GaussianHMM(n_components=3, covariance_type="full", n_iter=1000, random_state=42)
model_ret.fit(returns_data)
print(f"HMM Returns Done in {time.time() - start:.2f}s")

start = time.time()
diff_data = data[['Diff_Returns']].values
model_diff = hmm.GaussianHMM(n_components=3, covariance_type="full", n_iter=1000, random_state=42)
model_diff.fit(diff_data)
print(f"HMM Diff Done in {time.time() - start:.2f}s")
