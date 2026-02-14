import yfinance as yf
import pandas as pd
import numpy as np
import asyncio
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class DataProvider:
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=5)

    async def fetch_ticker_data(self, ticker: str, days: int = 365) -> pd.DataFrame:
        """
        Fetch data asynchronously using a thread pool to avoid blocking the main event loop.
        """
        loop = asyncio.get_event_loop()
        end_date = datetime.now() + timedelta(days=1)
        start_date = datetime.now() - timedelta(days=days)
        
        try:
            # Run blocking yfinance call in a separate thread
            data = await loop.run_in_executor(
                self.executor,
                self._fetch_sync,
                ticker,
                start_date,
                end_date
            )
            
            if data.empty:
                logger.warning(f"No data found for {ticker}")
                return pd.DataFrame()

            # Process data
            if isinstance(data.columns, pd.MultiIndex):
                data.columns = data.columns.get_level_values(0)
            
            # Calculate returns (CPU bound but fast enough for main thread usually, 
            # or could also be offloaded if data is massive)
            price_col = 'Close'
            data['Returns'] = np.log(data[price_col] / data[price_col].shift(1))
            data['Diff_Returns'] = data['Returns'].diff()
            data.dropna(inplace=True)
            
            return data
            
        except Exception as e:
            logger.error(f"Error fetching data for {ticker}: {e}")
            raise

    def _fetch_sync(self, ticker, start, end):
        """Internal synchronous method for yfinance"""
        ticker_obj = yf.Ticker(ticker)
        return ticker_obj.history(start=start, end=end, auto_adjust=True)

    def get_currency(self, ticker: str) -> str:
        try:
            return yf.Ticker(ticker).info.get('currency', 'USD')
        except:
            return 'USD'

# Global instance
data_provider = DataProvider()
