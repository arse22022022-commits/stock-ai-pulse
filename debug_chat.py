# Debug Chat Script
import os
import asyncio
import sys

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from dotenv import load_dotenv
load_dotenv('backend/.env')

from backend.app.services.chat import generate_market_explanation, ChatRequest

async def test_chat():
    api_key = os.getenv("GOOGLE_API_KEY")
    print(f"GOOGLE_API_KEY present: {bool(api_key)}")
    if api_key:
        print(f"Key length: {len(api_key)}")
        print(f"Key starts with: {api_key[:4]}...")

    req = ChatRequest(
        ticker="TEST",
        price=100.0,
        hmm_state="Alcista",
        impulse_state="Fuerte",
        user_query="Dame un resumen"
    )

    print("\nTesting generate_market_explanation...")
    try:
        response = await generate_market_explanation(req)
        print("\nResponse received:")
        print(response)
    except Exception as e:
        print(f"\nError: {e}")

if __name__ == "__main__":
    asyncio.run(test_chat())
