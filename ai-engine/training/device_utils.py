"""Pick best available device for Ultralytics on macOS / Linux / CUDA."""

import torch


def get_default_device() -> str:
    if torch.cuda.is_available():
        return "0"
    if getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
        return "mps"
    return "cpu"
