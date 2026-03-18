"""Focused debug for BC.MI R/R discrepancy"""
import os, sys
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"

import numpy as np, pandas as pd, yfinance as yf
from datetime import datetime, timedelta
from backend.app.services.analysis import train_hmm_returns, train_hmm_diff

ticker = "BC.MI"
end_date = datetime.now() + timedelta(days=1)
start_date = datetime.now() - timedelta(days=365)
t = yf.Ticker(ticker)
data = t.history(start=start_date, end=end_date, auto_adjust=True)
if isinstance(data.columns, pd.MultiIndex):
    data.columns = data.columns.get_level_values(0)
data['Returns'] = np.log(data['Close'] / data['Close'].shift(1))
data['Diff_Returns'] = data['Returns'].diff()
data['Vol_SMA'] = data['Volume'].rolling(window=20).mean()
data['RVOL'] = data['Volume'] / data['Vol_SMA']
data.dropna(inplace=True)

regimes_ret, probs_ret, final_ret_stats = train_hmm_returns(data)
current_regime_id = int(regimes_ret[-1])

print(f"=== BC.MI DIAGNOSTIC ===")
print(f"Data points: {len(data)}")
print(f"Current regime (smoothed): {current_regime_id}")
print()
for s in final_ret_stats:
    tag = " <<< CURRENT" if s['regime'] == current_regime_id else ""
    print(f"  Regime {s['regime']}: mean={s['mean']:.6f}%, std={s['std']:.6f}%, R/R={s['ratio_rr']:.6f}{tag}")

cs = next((s for s in final_ret_stats if s['regime'] == current_regime_id), {})
m = cs.get('mean', 0)
s = cs.get('std', 0)
rr = cs.get('ratio_rr', 0)
print(f"\nCURRENT: mean={m:.6f}, std={s:.6f}, ratio_rr={rr:.6f}")
print(f"Manual check: mean/std = {m/s if s != 0 else 'DIV0'}")
print(f"Sign consistency: mean>0={m>0}, rr>0={rr>0}, CONSISTENT={((m>0)==(rr>0)) or m==0}")
