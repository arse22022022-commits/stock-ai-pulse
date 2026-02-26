import requests, time
tickers = ["AAPL", "MSFT", "GOOG", "TSLA", "NVDA", "IBE.MC", "SAN.MC"]
print("Iniciando Test de Estrés Local...")
start = time.time()
try:
    res = requests.post("http://127.0.0.1:8000/api/portfolio", json=tickers, timeout=120)
    print(f"Status: {res.status_code}. Tiempo: {time.time()-start:.2f}s")
except Exception as e:
    print(f"Error: {e}")
