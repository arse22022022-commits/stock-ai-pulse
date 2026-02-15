import requests
import json
import sys

url = "http://localhost:8001/api/chat"
payload = {
    "ticker": "ACS.MC",
    "price": 40.5,
    "hmm_state": "Bullish",
    "impulse_state": "Neutral",
    "user_query": "Interpretalo"
}
headers = {'Content-Type': 'application/json'}

print(f"Testing {url}...")
try:
    response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=10)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print(f"Response: {response.json()['response'].encode('utf-8')}")
    else:
        print(f"Error Response: {response.text}")
except Exception as e:
    print(f"Exception: {e}")
