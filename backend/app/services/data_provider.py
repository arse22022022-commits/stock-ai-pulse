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

    async def fetch_ticker_data(self, ticker: str, days: int = 365) -> tuple[pd.DataFrame, str]:
        """
        Fetch data asynchronously using a thread pool to avoid blocking the main event loop.
        Returns: (DataFrame, currency_string)
        """
        loop = asyncio.get_event_loop()
        end_date = datetime.now() + timedelta(days=1)
        start_date = datetime.now() - timedelta(days=days)
        
        try:
            # Run blocking yfinance call in a separate thread
            data, currency = await loop.run_in_executor(
                self.executor,
                self._fetch_sync,
                ticker,
                start_date,
                end_date
            )
            
            if data.empty:
                logger.warning(f"No data found for {ticker}")
                return pd.DataFrame(), "USD"

            # Process data
            if isinstance(data.columns, pd.MultiIndex):
                data.columns = data.columns.get_level_values(0)
            
            # 1. Clean Index: ensure it is a simple datetime index without TZs if possible
            if data.index.tz is not None:
                data.index = data.index.tz_localize(None)
            
            # 2. Basic cleaning: drop rows with all NaNs or empty
            data = data.dropna(how='all')
            if data.empty: return pd.DataFrame(), "USD"
            
            # 3. Handle Prices: ensure 'Close' exists and is numeric
            price_col = 'Close'
            if price_col not in data.columns:
                # Try to find it case-insensitive
                matches = [c for c in data.columns if c.lower() == 'close']
                if matches: price_col = matches[0]
                else: return pd.DataFrame(), "USD"
            
            data[price_col] = pd.to_numeric(data[price_col], errors='coerce')
            data = data[data[price_col] > 0.01].copy() # Ignore pennies/zero prices
            
            # 4. Calculate technical columns
            data['Returns'] = np.log(data[price_col] / data[price_col].shift(1))
            data['Diff_Returns'] = data['Returns'].diff()
            
            # 5. Vol_SMA and RVOL
            data['Vol_SMA'] = data['Volume'].rolling(window=20).mean()
            # Safe RVOL calculation
            data['RVOL'] = (data['Volume'] / data['Vol_SMA'])
            
            # 6. EMA 10
            data['EMA_10'] = data[price_col].ewm(span=10, adjust=False).mean()
            
            # 7. FINAL ULTRA-CLEANUP: Replace all non-finite (Inf, NaN) with a safe default or drop
            # We target specific numeric columns that models use
            numeric_cols = ['Close', 'Returns', 'Diff_Returns', 'Volume', 'RVOL', 'EMA_10']
            for col in numeric_cols:
                if col in data.columns:
                    data[col] = data[col].replace([np.inf, -np.inf], np.nan)
            
            data = data.dropna(subset=['Returns', 'Diff_Returns', 'RVOL']).copy()
            
            # Fill remaining with neutral values
            if 'RVOL' in data.columns: data['RVOL'] = data['RVOL'].fillna(1.0)
            
            logger.info(f"DATADEBUG: {ticker} final shape: {data.shape}")
            return data, currency
            
        except Exception as e:
            logger.error(f"Error fetching data for {ticker}: {e}")
            raise

    def _fetch_sync(self, ticker, start, end):
        """Internal synchronous method for yfinance"""
        ticker_obj = yf.Ticker(ticker)
        df = ticker_obj.history(start=start, end=end, auto_adjust=True)
        try:
            # Use fast_info to avoid the slow/hanging .info call
            currency = ticker_obj.fast_info.get('currency', 'USD')
        except:
            currency = 'USD'
        return df, currency

# Global instance
data_provider = DataProvider()
