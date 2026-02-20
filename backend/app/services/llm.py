import logging
import os
import threading

import torch
import numpy as np
from datetime import timedelta

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self):
        self.pipeline = None
        self.enabled = False
        self.lock = threading.Lock()
        self._load_model()

    def _load_model(self):
        try:
            # Check environment variable to optionally disable LLM for faster local dev
            if os.getenv("DISABLE_LLM") == "true":
                logger.info("LLM disabled via environment variable")
                return

            logger.info("Attempting to load Chronos LLM...")
            # Lazy import to prevent import-time crashes
            from chronos import ChronosPipeline
            self.pipeline = ChronosPipeline.from_pretrained(
                "amazon/chronos-t5-tiny",
                device_map="cpu",
                torch_dtype=torch.float32,
            )
            self.enabled = True
            logger.info("Chronos LLM loaded successfully")
        except Exception as e:
            # CRITICAL: Catch ALL exceptions to prevent backend crash
            logger.error(f"Failed to load Chronos LLM: {str(e)}", exc_info=True)
            logger.warning("Forecasting will use statistical fallback due to LLM load failure.")
            self.enabled = False
            self.pipeline = None

    def predict(self, data_series: np.ndarray, prediction_length: int = 10, last_date=None, last_price=0.0):
        """
        Generate forecast. If LLM is active, use it. Otherwise, use statistical fallback.
        """
        forecast_result = []
        
        if self.enabled and self.pipeline:
            try:
                # CRITICAL: Synchronize access to the model
                # Chronos/Torch on CPU might not be thread-safe for concurrent inference
                with self.lock:
                    context = torch.tensor(data_series)
                    forecast = self.pipeline.predict(context, prediction_length)
                
                logger.info("Chronos forecast generated successfully.")
                
                # Calculate percentiles
                forecast_10th = np.quantile(forecast[0].numpy(), 0.1, axis=0)
                forecast_median = np.median(forecast[0].numpy(), axis=0)
                forecast_90th = np.quantile(forecast[0].numpy(), 0.9, axis=0)
                
                for i in range(prediction_length):
                    forecast_result.append({
                        "date": (last_date + timedelta(days=i+1)).strftime("%Y-%m-%d"),
                        "price": float(forecast_median[i]),
                        "price_low": float(forecast_10th[i]),
                        "price_high": float(forecast_90th[i]),
                        "type": "forecast"
                    })
                return forecast_result
            except Exception as e:
                logger.error(f"Chronos prediction failed: {e}. Falling back to statistical model.")
                # Fall through to fallback
        
        # Fallback: Geometric Brownian Motion
        # Using the last portion of the series to estimate parameters
        returns = np.diff(np.log(data_series[-60:])) # Use last 60 days for drift/vol
        mu = np.mean(returns)
        sigma = np.std(returns)
        
        for i in range(prediction_length):
            drift = np.exp((mu - 0.5 * sigma**2) * (i+1))
            uncertainty = 1.96 * sigma * np.sqrt(i+1)
            
            price_est = float(last_price * drift)
            forecast_result.append({
                "date": (last_date + timedelta(days=i+1)).strftime("%Y-%m-%d"), 
                "price": price_est,
                "price_low": float(price_est * np.exp(-uncertainty)),
                "price_high": float(price_est * np.exp(uncertainty)),
                "type": "forecast"
            })
            
        return forecast_result

    async def predict_async(self, data_series: np.ndarray, prediction_length: int = 10, last_date=None, last_price=0.0):
        """
        Async wrapper for predict to avoid blocking the main event loop.
        """
        import asyncio
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            None, # Use default executor
            self.predict,
            data_series,
            prediction_length,
            last_date,
            last_price
        )

# Global instance
llm_service = LLMService()
