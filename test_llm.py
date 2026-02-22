import os
os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"
import asyncio
import numpy as np
from datetime import datetime
from backend.app.services.llm import llm_service

async def test():
    print(f"LLM Enabled: {llm_service.enabled}")
    if llm_service.enabled:
        print(f"Model: {llm_service.model.model_name}")
    try:
        print("Calling predict_async...")
        res = await asyncio.wait_for(
            llm_service.predict_async(
                data_series=np.random.randn(60),
                prediction_length=10,
                last_date=datetime.now(),
                last_price=100.0
            ),
            timeout=15.0
        )
        print("Completed successfully!")
        print(res)
    except asyncio.TimeoutError:
        print("TIMEOUT - The SDK call is hanging!")
    except Exception as e:
        print(f"Exception: {type(e).__name__} - {e}")

if __name__ == "__main__":
    asyncio.run(test())
