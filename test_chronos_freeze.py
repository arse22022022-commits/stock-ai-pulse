import asyncio
import numpy as np

async def test():
    print("Testing Chronos multiple times from event loop...")
    from backend.app.services.llm import llm_service
    
    dummy_data = np.linspace(100, 150, 60)
    
    print("Attempt 1...")
    res1 = await llm_service.predict_async(dummy_data)
    print("Attempt 1 clear.")
    
    print("Attempt 2...")
    res2 = await llm_service.predict_async(dummy_data)
    print("Attempt 2 clear.")
    
if __name__ == '__main__':
    asyncio.run(test())
