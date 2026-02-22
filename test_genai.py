import os
import asyncio
from google import genai
from google.genai import types

async def main():
    client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))
    models_to_test = [
        "gemini-flash-latest", 
        "gemini-flash-lite-latest", 
        "gemini-pro-latest", 
        "gemini-2.5-flash-lite-preview-09-2025"
    ]
    
    for m in models_to_test:
        print(f"--- Testing {m} ---")
        successes = 0
        for i in range(5):
            try:
                response = await client.aio.models.generate_content(
                    model=m,
                    contents=f'Di hola iter {i}',
                    config=types.GenerateContentConfig(response_mime_type='text/plain')
                )
                successes += 1
            except Exception as e:
                print(f"Error at {i}: {e}")
                break
        print(f"Total: {successes}/5 for {m}")

if __name__ == "__main__":
    asyncio.run(main())
