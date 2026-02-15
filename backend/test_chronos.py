import sys
import os

# Fix for protobuf error
os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"

print(f"Starting script... Python: {sys.version}", flush=True)

try:
    print("Importing torch...", flush=True)
    import torch
    print(f"Torch imported. Version: {torch.__version__}", flush=True)

    print("Attempting to import chronos...", flush=True)
    from chronos import ChronosPipeline
    print("Import successful.", flush=True)
    
    print("Attempting to load model...", flush=True)
    pipeline = ChronosPipeline.from_pretrained(
        "amazon/chronos-t5-tiny",
        device_map="cpu",
        torch_dtype=torch.float32,
    )
    print("Model loaded successfully.", flush=True)
    
    # Test random prediction
    import numpy as np
    data = torch.tensor(np.random.rand(50))
    print("Attempting prediction...", flush=True)
    forecast = pipeline.predict(data, 10)
    print("Prediction successful.", flush=True)
    print(forecast.shape, flush=True)

except Exception as e:
    print(f"CRITICAL ERROR: {e}")
    import traceback
    traceback.print_exc()
