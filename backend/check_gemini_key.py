import os
import asyncio
from dotenv import load_dotenv
from google import genai

async def check_gemini():
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")
    model_name = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
    
    print(f"Testing with API Key: {api_key[:10]}...")
    print(f"Model: {model_name}")
    
    if not api_key:
        print("Error: GOOGLE_API_KEY not found in .env")
        return

    try:
        client = genai.Client(api_key=api_key)
        response = await client.aio.models.generate_content(
            model=model_name,
            contents="Hello, are you active?"
        )
        print("Success! Gemini response:")
        print(response.text)
    except Exception as e:
        print(f"Failed to connect to Gemini: {str(e)}")

if __name__ == "__main__":
    asyncio.run(check_gemini())
