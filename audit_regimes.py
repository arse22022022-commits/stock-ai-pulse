import requests
import json

ticker = "MTS.MC"
url = f"http://127.0.0.1:8000/api/analyze/{ticker}"

try:
    print(f"Fetching data for {ticker}...")
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        history = data.get('history', [])
        print(f"Total history points: {len(history)}")
        
        regimes = [item.get('regime') for item in history]
        unique_regimes = set(regimes)
        print(f"Unique regimes found: {unique_regimes}")
        
        # Count occurrences
        counts = {r: regimes.count(r) for r in unique_regimes}
        print(f"Regime counts: {counts}")
        
        if len(history) > 0:
            print(f"First 5 regimes: {regimes[:5]}")
            print(f"Last 5 regimes: {regimes[-5:]}")
            
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
except Exception as e:
    print(f"Exception: {e}")
