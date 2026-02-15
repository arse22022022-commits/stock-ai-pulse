from google import genai
import os
from dotenv import load_dotenv

load_dotenv("backend/.env")
api_key = os.getenv("GOOGLE_API_KEY")
print(f"Key: {api_key[:5]}..." if api_key else "No Key")

client = genai.Client(api_key=api_key)
try:
    # try to list models
    # The new SDK might use different call.
    # client.models.list() returns a pager of Model
    pager = client.models.list()
    for model in pager:
        print(model.name)
except Exception as e:
    print(f"Error: {e}")
