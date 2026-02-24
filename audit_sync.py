import requests
import json
import random

ticker = "MTS.MC"
# Cache bypass with random param
url = f"http://127.0.0.1:8000/api/analyze/{ticker}?cb={random.random()}"

try:
    print(f"Fetching data for {ticker} (Bypassing cache)...")
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        
        # Dashboard Verdict
        ai_rec = data.get('recommendation', {})
        verdict = ai_rec.get('verdict')
        score = ai_rec.get('score')
        
        # Chart Strategy (History)
        history = data.get('history', [])
        last_point = history[-1] if history else {}
        last_regime = last_point.get('regime')
        
        print("\n--- CONSISTENCY CHECK ---")
        print(f"Dashboard Verdict: {verdict} (Score: {score})")
        print(f"Chart Last State: {last_regime} (0:Hold, 1:Buy, 2:Sell)")
        
        # Logic check
        is_consistent = False
        if last_regime == 1 and "COMPRA" in verdict: is_consistent = True
        elif last_regime == 0 and "MANTENER" in verdict: is_consistent = True
        elif last_regime == 2 and "VENTA" in verdict: is_consistent = True
        
        if is_consistent:
            print("✅ SUCCESS: Verdict and Chart are SYNCHRONIZED.")
        else:
            print(f"❌ FAILURE: CONTRADICTION DETECTED. Verdict: {verdict}, Regime: {last_regime}")
            
    else:
        print(f"Error: {response.status_code}")
except Exception as e:
    print(f"Exception: {e}")
