import os
from google import genai
from dotenv import load_dotenv

def list_models():
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("No API key found.")
        return
    
    try:
        client = genai.Client(api_key=api_key)
        print("Available models:")
        for model in client.models.list():
            print(f"- {model.name} (Display: {model.display_name})")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    list_models()
