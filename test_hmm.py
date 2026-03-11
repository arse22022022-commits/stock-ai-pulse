import asyncio

async def test():
    print("Testing data fetching + HMM...")
    from backend.app.services.data_provider import data_provider
    from backend.app.services.analysis import train_hmm_returns, train_hmm_diff
    
    print('fetching data...')
    data, _ = await data_provider.fetch_ticker_data('SAN.MC')
    print('training HMM...')
    
    loop = asyncio.get_running_loop()
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=2) as executor:
        hmm_tasks = [
            loop.run_in_executor(executor, train_hmm_returns, data),
            loop.run_in_executor(executor, train_hmm_diff, data)
        ]
        hmm_results = await asyncio.gather(*hmm_tasks)
    
    print('done HMM!')

if __name__ == '__main__':
    asyncio.run(test())
