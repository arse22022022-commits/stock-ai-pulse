import urllib.request
import json
import time

url = "http://127.0.0.1:8001/api/health" # Or just /health depending on mount. main.py has @app.get("/health")
try:
    with urllib.request.urlopen("http://127.0.0.1:8001/health") as response:
        data = json.loads(response.read().decode())
        print(f"Health Check: {data}")
        if data.get("llm_enabled"):
            print("SUCCESS: LLM is ENABLED.")
        else:
            print("FAILURE: LLM is DISABLED.")
except Exception as e:
    print(f"Health check failed: {e}")
