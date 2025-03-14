#!/usr/bin/env python3
"""
Dependency checker for the Automated Audio Drama Generator.

This script verifies that all required dependencies are correctly installed
and provides information about any missing or incompatible dependencies.
"""

import os
import sys
import importlib.util
import pkg_resources
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple, Set

# Define required packages with their minimum versions
REQUIRED_PACKAGES = {
  # Core dependencies
  "numpy": "1.22.0",
  "torch": "1.12.0",
  "torchaudio": "0.12.0",
  "transformers": "4.20.0",
  "pydub": "0.25.1",
  "librosa": "0.9.2",
  "soundfile": "0.10.3",
  "scipy": "1.8.0",
  "matplotlib": "3.5.0",

  # Script parsing
  "markdown": "3.3.0",
  "beautifulsoup4": "4.10.0",
  "regex": "2022.3.0",

  # Audio processing
  "audiomentations": "0.20.0",
  "pedalboard": "0.5.0",

  # TTS/Voice models
  "huggingface_hub": "0.10.0",
  "onnxruntime": "1.11.0",
  "speechbrain": "0.5.12",

  # Testing
  "pytest": "7.0.0",
  "pytest-cov": "2.12.0",

  # Utilities
  "tqdm": "4.64.0",
  "click": "8.1.0",
  "PyYAML": "6.0.0",
  "joblib": "1.1.0"
}

# Optional packages
OPTIONAL_PACKAGES = {
  "onnxruntime-gpu": "1.11.0",  # GPU acceleration for ONNX
  "cupy": "10.0.0",              # GPU acceleration for numerical computations
  "numba": "0.55.0"              # JIT compilation for numerical computations
}

def check_package(package_name: str, min_version: str) -> Tuple[bool, str]:
  """
  Check if a package is installed and meets the minimum version requirement.

  Args:
      package_name (str): Name of the package
      min_version (str): Minimum required version

  Returns:
      tuple: (is_compatible, message)
  """
  try:
    # Get the installed version
    installed_version = pkg_resources.get_distribution(package_name).version

    # Check if the installed version meets the minimum requirement
    is_compatible = pkg_resources.parse_version(installed_version) >= pkg_resources.parse_version(min_version)

    if is_compatible:
      return True, f"{package_name} {installed_version} (>= {min_version}) ✓"
    else:
      return False, f"{package_name} {installed_version} (< {min_version}) ✗"

  except pkg_resources.DistributionNotFound:
    return False, f"{package_name} not installed ✗"
  except Exception as e:
    return False, f"{package_name} error: {str(e)} ✗"

def check_all_packages() -> Tuple[List[str], List[str], List[str]]:
  """
  Check all required and optional packages.

  Returns:
      tuple: (ok_messages, warning_messages, error_messages)
  """
  ok_messages = []
  warning_messages = []
  error_messages = []

  # Check required packages
  print("Checking required packages...")
  for package_name, min_version in REQUIRED_PACKAGES.items():
    is_compatible, message = check_package(package_name, min_version)
    print(f"  {message}")

    if is_compatible:
      ok_messages.append(message)
    else:
      error_messages.append(message)

  # Check optional packages
  print("\nChecking optional packages...")
  for package_name, min_version in OPTIONAL_PACKAGES.items():
    is_compatible, message = check_package(package_name, min_version)
    print(f"  {message}")

    if is_compatible:
      ok_messages.append(message)
    else:
      warning_messages.append(message)

  return ok_messages, warning_messages, error_messages

def check_pytorch_cuda() -> bool:
  """
  Check if PyTorch CUDA is available.

  Returns:
      bool: True if PyTorch CUDA is available
  """
  try:
    import torch
    has_cuda = torch.cuda.is_available()

    if has_cuda:
      device_count = torch.cuda.device_count()
      cuda_version = torch.version.cuda

      print(f"\nPyTorch CUDA: Available (version {cuda_version}) ✓")
      print(f"  Found {device_count} CUDA device(s)")

      for i in range(device_count):
        device_name = torch.cuda.get_device_name(i)
        print(f"  - Device {i}: {device_name}")

      return True
    else:
      print("\nPyTorch CUDA: Not available ✗")
      return False

  except Exception as e:
    print(f"\nPyTorch CUDA: Error checking availability: {str(e)} ✗")
    return False

def check_onnx_runtime() -> bool:
  """
  Check ONNX Runtime providers.

  Returns:
      bool: True if ONNX Runtime has GPU providers
  """
  try:
    import onnxruntime as ort
    providers = ort.get_available_providers()

    print("\nONNX Runtime providers:")
    for provider in providers:
      print(f"  - {provider}")

    has_gpu = any(p.startswith("CUDA") or p.startswith("GPU") for p in providers)
    if has_gpu:
      print("ONNX Runtime GPU: Available ✓")
    else:
      print("ONNX Runtime GPU: Not available ✗")

    return has_gpu

  except Exception as e:
    print(f"\nONNX Runtime: Error checking providers: {str(e)} ✗")
    return False

def check_disk_space(min_space_gb: float = 5.0) -> bool:
  """
  Check available disk space.

  Args:
      min_space_gb (float): Minimum required disk space in GB

  Returns:
      bool: True if sufficient disk space is available
  """
  try:
    # Get the directory of this script
    script_dir = Path(__file__).parent.absolute()

    # Get disk usage statistics
    if os.name == 'posix':
      # Unix-like
      import shutil
      total, used, free = shutil.disk_usage(script_dir)
    else:
      # Windows
      import ctypes
      free_bytes = ctypes.c_ulonglong(0)
      ctypes.windll.kernel32.GetDiskFreeSpaceExW(ctypes.c_wchar_p(str(script_dir)), None, None, ctypes.pointer(free_bytes))
      free = free_bytes.value

    # Convert to GB
    free_gb = free / (1024**3)

    print(f"\nAvailable disk space: {free_gb:.2f} GB")

    if free_gb >= min_space_gb:
      print(f"Disk space: Sufficient (>= {min_space_gb} GB) ✓")
      return True
    else:
      print(f"Disk space: Insufficient (< {min_space_gb} GB) ✗")
      return False

  except Exception as e:
    print(f"Disk space: Error checking availability: {str(e)} ✗")
    return False

def check_python_version(min_version: Tuple[int, int] = (3, 9)) -> bool:
  """
  Check Python version.

  Args:
      min_version (tuple): Minimum required Python version (major, minor)

  Returns:
      bool: True if Python version meets the minimum requirement
  """
  major, minor = sys.version_info[:2]

  print(f"\nPython version: {major}.{minor}")

  if (major, minor) >= min_version:
    print(f"Python version: Sufficient (>= {min_version[0]}.{min_version[1]}) ✓")
    return True
  else:
    print(f"Python version: Insufficient (< {min_version[0]}.{min_version[1]}) ✗")
    return False

def main():
  """Run the dependency checker."""
  print("=== Dependency Checker for Audio Drama Generator ===\n")

  # Check Python version
  python_ok = check_python_version()

  # Check packages
  ok_messages, warning_messages, error_messages = check_all_packages()

  # Check PyTorch CUDA
  pytorch_cuda_ok = check_pytorch_cuda()

  # Check ONNX Runtime
  onnx_runtime_ok = check_onnx_runtime()

  # Check disk space
  disk_space_ok = check_disk_space()

  # Summarize results
  print("\n=== Summary ===")
  print(f"Required packages: {len(ok_messages)}/{len(REQUIRED_PACKAGES)} installed and compatible")
  print(f"Optional packages: {len(ok_messages) + len(warning_messages) - len(REQUIRED_PACKAGES)}/{len(OPTIONAL_PACKAGES)} installed and compatible")
  print(f"PyTorch CUDA: {'Available' if pytorch_cuda_ok else 'Not available'}")
  print(f"ONNX Runtime GPU: {'Available' if onnx_runtime_ok else 'Not available'}")
  print(f"Disk space: {'Sufficient' if disk_space_ok else 'Insufficient'}")
  print(f"Python version: {'Compatible' if python_ok else 'Incompatible'}")

  # Print error messages
  if error_messages:
    print("\n=== Required Dependencies Issues ===")
    for message in error_messages:
      print(f"  {message}")
    print("\nPlease install or update these required dependencies.")

  # Print warning messages
  if warning_messages:
    print("\n=== Optional Dependencies Issues ===")
    for message in warning_messages:
      print(f"  {message}")
    print("\nThese dependencies are optional but recommended for better performance.")

  # Final verdict
  if error_messages:
    print("\nVerdict: Some required dependencies are missing or incompatible.")
    return 1
  else:
    print("\nVerdict: All required dependencies are installed and compatible.")
    if warning_messages:
      print("Some optional dependencies are missing or incompatible.")
    return 0

if __name__ == "__main__":
  sys.exit(main())