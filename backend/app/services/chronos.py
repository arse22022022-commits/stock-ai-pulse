import logging
import numpy as np
import torch
from chronos import ChronosPipeline

logger = logging.getLogger(__name__)

class ChronosService:
    def __init__(self):
        # Limit torch threads to prevent deadlocks and contention on Windows/Cloud Run
        torch.set_num_threads(1)
        if torch.get_num_interop_threads() > 1:
            torch.set_num_interop_threads(1)
        
        self.pipeline = None
        self.enabled = False
        self._load_model()

    def _load_model(self):
        try:
            # Force thread limit again during model load
            torch.set_num_threads(1)
            
            # Load the smallest Chronos model to conserve memory in Cloud Run
            device = "cpu" 
            self.pipeline = ChronosPipeline.from_pretrained(
                "amazon/chronos-t5-tiny",
                device_map=device,
                torch_dtype=torch.float32,
            )
            self.enabled = True
            logger.info(f"Chronos (Local LLM) initialized successfully on {device} (threads limited to 1)")
        except Exception as e:
            logger.warning(f"Chronos model failed to load: {e}. High-fidelity fallback disabled.")
            self.enabled = False

    def predict(self, data_series: np.ndarray, prediction_length: int = 10):
        if not self.enabled or self.pipeline is None:
            return None
        
        try:
            # Prepare context for Chronos (needs a tensor)
            # FORCE FINITE: extreme safety for tickers like EOAN.DE
            clean_data = np.nan_to_num(data_series.astype(np.float32), nan=0.0, posinf=0.0, neginf=0.0)
            context = torch.tensor(clean_data)
            
            # Generate forecast
            # IMPORTANT: Ensure no threading conflicts during prediction
            torch.set_num_threads(1)
            torch.manual_seed(42) # FORCE ULTIMATE DETERMINISM in ancestral sampling
            with torch.no_grad():
                forecast = self.pipeline.predict(context, prediction_length)
            
            logger.info(f"CHRONOSDEBUG: Forecast shape: {forecast.shape}, Requested: {prediction_length}")
            
            # forecast shape is [num_series, prediction_length, num_samples/percentiles]
            median = forecast[0, :, 1].numpy()
            low = forecast[0, :, 0].numpy()
            high = forecast[0, :, 2].numpy()
            
            # Ensure we only return the requested length exactly
            # Some model versions or configurations might return more steps
            res_prices = [float(p) for p in median][:prediction_length]
            res_lows = [float(p) for p in low][:prediction_length]
            res_highs = [float(p) for p in high][:prediction_length]
            
            return {
                "prices": res_prices,
                "lows": res_lows,
                "highs": res_highs
            }
        except Exception as e:
            logger.error(f"Chronos prediction failed: {e}")
            return None

# Singleton instance
chronos_service = ChronosService()
