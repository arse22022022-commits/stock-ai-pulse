import os
import asyncio
from dotenv import load_dotenv
from google import genai

async def check_gemini_specific():
    # Load root .env
    load_dotenv(".env")
    api_key = os.getenv("GOOGLE_API_KEY")
    model_name = "gemini-2.5-flash-lite-preview-09-2025"
    
    print(f"Testing with API Key: {api_key[:10]}...")
    print(f"Model: {model_name}")
    
    try:
        client = genai.Client(api_key=api_key)
        response = await client.aio.models.generate_content(
            model=model_name,
            contents="Hello?"
        )
        print("Success!")
    except Exception as e:
        print(f"Failed: {str(e)}")

if __name__ == "__main__":
    asyncio.run(check_gemini_specific())
