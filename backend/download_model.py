from chronos import ChronosPipeline
import torch
import os

print("Downloading Chronos model to cache...")
# Force CPU for build phase
pipeline = ChronosPipeline.from_pretrained(
    "amazon/chronos-t5-tiny",
    device_map="cpu",
    torch_dtype=torch.float32,
)
print("Model downloaded successfully.")
