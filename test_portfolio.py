import requests
import time

tickers = ["SAN.MC", "BBVA.MC", "REP.MC", "IBE.MC", "ITX.MC", "TEF.MC"]
print(f"Testing portfolio endpoint with {len(tickers)} tickers...")
start_time = time.time()
try:
    response = requests.post("http://127.0.0.1:8000/api/portfolio", json=tickers, timeout=30)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Success! Analyzed {data['summary']['total_assets']} assets.")
        print(f"Advice: {data['summary']['advice']}")
    else:
        print(f"Error: {response.text}")
except Exception as e:
    print(f"Request failed: {e}")
print(f"Total time taken: {time.time() - start_time:.2f} seconds")
