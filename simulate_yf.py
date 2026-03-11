import asyncio

async def test_yfinance_concurrent():
    print("Testing yfinance concurrent...")
    from backend.app.services.data_provider import data_provider
    try:
        await asyncio.wait_for(
            asyncio.gather(
                data_provider.fetch_ticker_data("NVDA", 365),
                data_provider.fetch_ticker_data("SAN.MC", 365)
            ),
            timeout=15
        )
        print("YFinance Concurrent Completed!")
    except asyncio.TimeoutError:
        print("TIMEOUT! YFinance deadlocked")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_yfinance_concurrent())
