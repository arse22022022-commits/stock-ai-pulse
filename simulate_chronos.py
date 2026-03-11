import asyncio
import numpy as np

async def test_chronos_concurrent():
    print("Testing Chronos concurrent...")
    from backend.app.services.llm import llm_service
    dummy_data = np.linspace(100, 150, 60)
    try:
        await asyncio.wait_for(
            asyncio.gather(
                llm_service.predict_async(dummy_data, prediction_length=10, last_date="2025-01-01", last_price=150.0),
                llm_service.predict_async(dummy_data, prediction_length=10, last_date="2025-01-01", last_price=150.0)
            ),
            timeout=15
        )
        print("Chronos Concurrent Completed!")
    except asyncio.TimeoutError:
        print("TIMEOUT! Chronos deadlocked!")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_chronos_concurrent())
