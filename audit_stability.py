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
        print(f"Unique verdict-states found: {unique_regimes} (0:Hold, 1:Buy, 2:Sell)")
        
        # Count changes
        changes = 0
        for i in range(1, len(regimes)):
            if regimes[i] != regimes[i-1]:
                changes += 1
        
        print(f"Total state changes: {changes}")
        print(f"Stability index: {100 - (changes/len(history)*100):.2f}%")
        
        # Count occurrences
        counts = {r: regimes.count(r) for r in unique_regimes}
        print(f"Verdict counts: {counts}")
        
    else:
        print(f"Error: {response.status_code}")
except Exception as e:
    print(f"Exception: {e}")
