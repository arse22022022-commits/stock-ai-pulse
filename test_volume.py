import asyncio
import pandas as pd
from backend.app.services.data_provider import data_provider
from backend.app.services.analysis import train_hmm_returns, train_hmm_diff, generate_ai_recommendation

async def test_volume_integration():
    ticker = "AAPL"
    print(f"--- Testing Volume Integration for {ticker} ---")
    
    # 1. Fetch data
    data, currency = await data_provider.fetch_ticker_data(ticker)
    if data.empty:
        print("Error: No data fetched")
        return
    
    print(f"Data fetched: {len(data)} rows")
    print(f"Columns: {data.columns.tolist()}")
    print(f"Last RVOL: {data['RVOL'].iloc[-1]:.2f}")
    
    # 2. Run HMM
    reg_ret, probs_ret, stats_ret = train_hmm_returns(data)
    reg_diff, probs_diff, stats_diff = train_hmm_diff(data)
    
    # 3. Mock forecast (since we only want to test the recommendation logic)
    mock_forecast = [
        {"date": "2024-01-01", "price": 100},
        {"date": "2024-01-10", "price": 105}
    ]
    
    # 4. Generate recommendation
    rec = generate_ai_recommendation(
        data, reg_ret, reg_diff, probs_ret, probs_diff, 
        mock_forecast, stats_ret, stats_diff
    )
    
    print("\n--- Recommendation Result ---")
    print(f"Verdict: {rec['verdict']}")
    print(f"Score: {rec['score']}")
    print(f"Pillars Breakdown: {rec['scores']}")
    print(f"Reason: {rec['reason']}")

if __name__ == "__main__":
    asyncio.run(test_volume_integration())
