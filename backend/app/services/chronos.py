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
            context = torch.tensor(data_series)
            
            # Generate forecast
            # IMPORTANT: Ensure no threading conflicts during prediction
            torch.set_num_threads(1)
            with torch.no_grad():
                forecast = self.pipeline.predict(context, prediction_length)
            
            # forecast shape is [num_series, prediction_length, num_samples/percentiles]
            # amazon/chronos-t5-tiny returns 3 percentiles: 0.1, 0.5, 0.9
            median = forecast[0, :, 1].numpy()
            low = forecast[0, :, 0].numpy()
            high = forecast[0, :, 2].numpy()
            
            return {
                "prices": [float(p) for p in median],
                "lows": [float(p) for p in low],
                "highs": [float(p) for p in high]
            }
        except Exception as e:
            logger.error(f"Chronos prediction failed: {e}")
            return None

# Singleton instance
chronos_service = ChronosService()
