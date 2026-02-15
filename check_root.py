import requests
try:
    response = requests.get("http://localhost:8001/")
    print(f"Root Status: {response.status_code}")
    print(f"Content Start: {response.text[:100]}")
except Exception as e:
    print(f"Error: {e}")
