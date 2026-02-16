
import numpy as np
import pandas as pd
from hmmlearn import hmm

def train_and_predict(data, train_on_full=True):
    # Prepare data
    returns = np.log(data / data.shift(1)).dropna().values.reshape(-1, 1)
    
    model = hmm.GaussianHMM(n_components=3, covariance_type="full", n_iter=1000, random_state=42)
    
    if train_on_full:
        model.fit(returns)
    else:
        # Train on all EXCEPT the last point
        model.fit(returns[:-1])
        
    # Predict on ALL
    states = model.predict(returns)
    return states[-1]

# Generate synthetic trending data
np.random.seed(42)
dates = pd.date_range(start="2023-01-01", periods=100)
prices = [100]
for _ in range(99):
    prices.append(prices[-1] * (1 + np.random.normal(0.001, 0.01)))

base_series = pd.Series(prices)

print("--- STABILITY TEST ---")
print("Simulating 5 ticks for the last candle...")

print("\nMethod A: Train on FULL data (Current Implementation)")
results_a = []
for tick in [-0.005, -0.002, 0.0, 0.002, 0.005]: # -0.5% to +0.5% fluctuation
    current_series = base_series.copy()
    current_series.iloc[-1] = current_series.iloc[-1] * (1 + tick)
    state = train_and_predict(current_series, train_on_full=True)
    results_a.append(state)
    print(f"Tick {tick*100:+.1f}%: State {state}")

print("\nMethod B: Train on CLOSED data (History[:-1])")
results_b = []
for tick in [-0.005, -0.002, 0.0, 0.002, 0.005]:
    current_series = base_series.copy()
    current_series.iloc[-1] = current_series.iloc[-1] * (1 + tick)
    state = train_and_predict(current_series, train_on_full=False)
    results_b.append(state)
    print(f"Tick {tick*100:+.1f}%: State {state}")

is_stable_a = len(set(results_a)) == 1
is_stable_b = len(set(results_b)) == 1

print(f"\nMethod A Stable? {is_stable_a}")
print(f"Method B Stable? {is_stable_b}")
