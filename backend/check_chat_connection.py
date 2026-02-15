import os
from google import genai
import logging
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv(".env")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

print(f"Key loaded: {bool(GOOGLE_API_KEY)}")

try:
    client = genai.Client(api_key=GOOGLE_API_KEY)
    response = client.models.generate_content(
        model='gemini-2.0-flash',
        contents='Hola, ¿estás funcionando?'
    )
    print("SUCCESS")
    print(response.text)
except Exception as e:
    print("FAILURE")
    print(e)
    # Check if it's a protobuf error
    import traceback
    traceback.print_exc()
