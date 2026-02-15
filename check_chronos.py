import logging
import torch
import numpy as np
import os
import sys

# Configure logging to stdout
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_chronos():
    logger.info("Starting Chronos verification...")
    
    try:
        from chronos import ChronosPipeline
        logger.info("Successfully imported ChronosPipeline")
    except ImportError as e:
        logger.error(f"Failed to import ChronosPipeline: {e}")
        logger.info("Detailed explanation: The 'chronos' package is missing. This means the system is falling back to statistical methods (Geometric Brownian Motion).")
        return False

    try:
        logger.info("Attempting to load model 'amazon/chronos-t5-tiny'...")
        pipeline = ChronosPipeline.from_pretrained(
            "amazon/chronos-t5-tiny",
            device_map="cpu",
            torch_dtype=torch.float32,
        )
        logger.info("Successfully loaded Chronos model!")
        
        # Test prediction
        logger.info("Testing prediction with dummy data...")
        dummy_data = torch.tensor(np.random.rand(1, 60).astype(np.float32)) # 60 days
        forecast = pipeline.predict(dummy_data, 10)
        logger.info(f"Prediction successful. Shape: {forecast.shape}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to load or run Chronos model: {e}")
        return False

if __name__ == "__main__":
    success = check_chronos()
    if success:
        sys.exit(0)
    else:
        sys.exit(1)
