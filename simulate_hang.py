import traceback
import asyncio
from backend.app.api.endpoints import analyze_stock

async def simulate_multiple_requests():
    print("Simulating Request 1: NVDA...")
    res1 = await analyze_stock("NVDA", lite_mode=False)
    print("NVDA finished!")
    
    print("Simulating Request 2: SAN.MC...")
    try:
        res2 = await asyncio.wait_for(analyze_stock("SAN.MC", lite_mode=False), timeout=30)
        print("SAN.MC finished!")
    except asyncio.TimeoutError:
        print("TIMEOUT! analyze_stock hung for >30 seconds on SAN.MC!")
    except Exception as e:
        print(f"Exception: {e}")
        traceback.print_exc()

if __name__ == '__main__':
    asyncio.run(simulate_multiple_requests())
