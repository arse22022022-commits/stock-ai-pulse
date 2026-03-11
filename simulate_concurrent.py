import asyncio
from backend.app.api.endpoints import analyze_stock

async def simulate_multithread_requests():
    print("Simulating concurrent requests NVDA and SAN.MC...")
    try:
        await asyncio.wait_for(
            asyncio.gather(
                analyze_stock("NVDA", lite_mode=False),
                analyze_stock("SAN.MC", lite_mode=False)
            ),
            timeout=30
        )
        print("CONCURRENT FINISHED!")
    except asyncio.TimeoutError:
        print("TIMEOUT! Concurrent execution deadlocked >30 seconds!")
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == '__main__':
    asyncio.run(simulate_multithread_requests())
