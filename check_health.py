import requests
try:
    response = requests.get("http://localhost:8001/health")
    print(f"Health Check: {response.status_code} - {response.text}")
except Exception as e:
    print(f"Error: {e}")
