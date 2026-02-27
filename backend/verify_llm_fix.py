import os
os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"
import asyncio
from dotenv import load_dotenv
import sys

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), "backend", "app"))
sys.path.append(os.getcwd())

async def verify_fix():
    print("Pre-loading check...")
    # Import service BEFORE loading dotenv to simulate race condition
    from backend.app.services.llm import llm_service
    print(f"Initial state - Enabled: {llm_service.enabled}")
    
    print("\nLoading environment...")
    load_dotenv(".env")
    print(f"API Key present: {bool(os.getenv('GOOGLE_API_KEY'))}")
    
    print("\nTriggering lazy load...")
    # This should trigger _load_model via is_active()
    active = llm_service.is_active()
    print(f"Active after lazy load: {active}")
    print(f"Enabled after lazy load: {llm_service.enabled}")
    
    if active:
        print("\nVerifying chat functionality...")
        context = {
            "ticker": "AAPL",
            "price": 150.0,
            "hmm_state": "Alcista",
            "impulse_state": "Fuerte",
            "user_query": "Hola, ¿cómo ves esta acción?"
        }
        response = await llm_service.generate_market_explanation_async(context)
        print("Gemini Response snippet:")
        print(response[:100] + "...")
    else:
        print("\nFAILED: LLM service did not activate.")

if __name__ == "__main__":
    asyncio.run(verify_fix())
