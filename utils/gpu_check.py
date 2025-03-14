#!/usr/bin/env python3
"""
GPU capability check for the Automated Audio Drama Generator.

This script checks if GPU acceleration is available and provides information about it.
"""

import os
import sys
import platform
import logging

# Setup logging
logging.basicConfig(
  level=logging.INFO,
  format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
  handlers=[
    logging.StreamHandler(sys.stdout)
  ]
)

logger = logging.getLogger(__name__)

def check_pytorch_gpu():
  """Check PyTorch GPU capabilities."""
  try:
    import torch

    if not torch.cuda.is_available():
      logger.warning("PyTorch: CUDA is not available. GPU acceleration will be disabled.")
      return False

    logger.info(f"PyTorch: CUDA is available (version {torch.version.cuda})")
    device_count = torch.cuda.device_count()
    logger.info(f"PyTorch: Found {device_count} CUDA device(s)")

    for i in range(device_count):
      device_name = torch.cuda.get_device_name(i)
      device_capability = torch.cuda.get_device_capability(i)
      logger.info(f"PyTorch: CUDA Device {i}: {device_name} (Compute Capability {device_capability[0]}.{device_capability[1]})")

    # Check current device
    current_device = torch.cuda.current_device()
    logger.info(f"PyTorch: Current CUDA device: {current_device} ({torch.cuda.get_device_name(current_device)})")

    # Test a small operation on GPU
    logger.info("PyTorch: Testing GPU computation...")
    x = torch.rand(100, 100, device="cuda")
    y = torch.rand(100, 100, device="cuda")
    z = x @ y  # Matrix multiplication
    z = z.cpu()  # Move back to CPU
    logger.info("PyTorch: GPU computation test successful")

    return True

  except Exception as e:
    logger.error(f"PyTorch: Error checking GPU capabilities: {str(e)}")
    return False

def check_onnx_gpu():
  """Check ONNX Runtime GPU capabilities."""
  try:
    import onnxruntime as ort

    providers = ort.get_available_providers()
    logger.info(f"ONNX Runtime: Available providers: {providers}")

    has_gpu = any(p.startswith("CUDA") or p.startswith("GPU") for p in providers)
    if not has_gpu:
      logger.warning("ONNX Runtime: No GPU providers available")
      return False

    logger.info("ONNX Runtime: GPU acceleration is available")

    # Get more details about the execution providers
    for provider in providers:
      if provider.startswith("CUDA"):
        logger.info(f"ONNX Runtime: {provider} provider is available")

    return True

  except Exception as e:
    logger.error(f"ONNX Runtime: Error checking GPU capabilities: {str(e)}")
    return False

def check_system_info():
  """Print system information."""
  logger.info(f"System: Python {platform.python_version()}")
  logger.info(f"System: {platform.system()} {platform.release()} ({platform.platform()})")
  logger.info(f"System: {platform.processor()}")

  # Try to get more detailed GPU information on Linux
  if platform.system() == "Linux":
    try:
      import subprocess
      result = subprocess.run(["nvidia-smi"], capture_output=True, text=True)
      if result.returncode == 0:
        logger.info(f"System: NVIDIA GPU detected\n{result.stdout}")
      else:
        logger.warning("System: nvidia-smi command failed, NVIDIA GPU may not be present")
    except:
      logger.warning("System: Could not run nvidia-smi")

def main():
  """Run the GPU capability checks."""
  logger.info("Checking GPU capabilities...")

  check_system_info()

  pytorch_gpu = check_pytorch_gpu()
  onnx_gpu = check_onnx_gpu()

  if pytorch_gpu or onnx_gpu:
    logger.info("GPU acceleration is available!")
    if pytorch_gpu:
      logger.info("- PyTorch GPU: Yes")
    else:
      logger.info("- PyTorch GPU: No")

    if onnx_gpu:
      logger.info("- ONNX Runtime GPU: Yes")
    else:
      logger.info("- ONNX Runtime GPU: No")

    return 0
  else:
    logger.warning("No GPU acceleration is available. The application will run slower.")
    logger.warning("To use GPU acceleration, please ensure you have a CUDA-compatible GPU")
    logger.warning("and that the appropriate CUDA toolkit is installed.")
    return 1

if __name__ == "__main__":
  sys.exit(main())