#!/usr/bin/env python3
"""
Environment verification tests for the Automated Audio Drama Generator.

This script verifies that the environment is correctly set up and
all dependencies are properly installed.
"""

import os
import sys
import importlib
import platform
import unittest
import tempfile
import subprocess
from pathlib import Path

class EnvironmentTests(unittest.TestCase):
  """Tests for verifying the environment setup."""

  def test_python_version(self):
    """Test that Python version is correct."""
    major, minor = sys.version_info[:2]
    self.assertGreaterEqual(major, 3, "Python major version must be 3 or higher")
    self.assertGreaterEqual(minor, 9, "Python minor version must be 9 or higher")

  def test_core_dependencies(self):
    """Test that core dependencies are installed."""
    dependencies = [
      "numpy",
      "torch",
      "torchaudio",
      "transformers",
      "pydub",
      "librosa",
      "soundfile",
      "scipy",
      "matplotlib"
    ]

    for dep in dependencies:
      try:
        importlib.import_module(dep)
      except ImportError:
        self.fail(f"Dependency {dep} is not installed")

  def test_script_parsing_dependencies(self):
    """Test that script parsing dependencies are installed."""
    dependencies = [
      "markdown",
      "bs4",  # beautifulsoup4
      "regex"
    ]

    for dep in dependencies:
      try:
        importlib.import_module(dep)
      except ImportError:
        self.fail(f"Dependency {dep} is not installed")

  def test_audio_processing_dependencies(self):
    """Test that audio processing dependencies are installed."""
    dependencies = [
      "audiomentations",
      "pedalboard",
      "wave"
    ]

    for dep in dependencies:
      try:
        importlib.import_module(dep)
      except ImportError:
        self.fail(f"Dependency {dep} is not installed")

  def test_tts_dependencies(self):
    """Test that TTS dependencies are installed."""
    dependencies = [
      "huggingface_hub",
      "onnxruntime",
      "speechbrain"
    ]

    for dep in dependencies:
      try:
        importlib.import_module(dep)
      except ImportError:
        self.fail(f"Dependency {dep} is not installed")

  def test_utility_dependencies(self):
    """Test that utility dependencies are installed."""
    dependencies = [
      "tqdm",
      "click",
      "yaml",
      "joblib"
    ]

    for dep in dependencies:
      try:
        if dep == "yaml":
          importlib.import_module("yaml")
        else:
          importlib.import_module(dep)
      except ImportError:
        self.fail(f"Dependency {dep} is not installed")

  def test_pytorch_gpu_availability(self):
    """Test if PyTorch can detect a GPU (if available)."""
    try:
      import torch
      # This just tests if CUDA is available, doesn't fail if not
      has_cuda = torch.cuda.is_available()
      if not has_cuda:
        print("\nWARNING: PyTorch CUDA not available. GPU acceleration will be disabled.")
      else:
        print(f"\nINFO: PyTorch CUDA available: {torch.version.cuda}")
        print(f"INFO: CUDA device count: {torch.cuda.device_count()}")
        if torch.cuda.device_count() > 0:
          print(f"INFO: Current CUDA device: {torch.cuda.get_device_name(0)}")
    except Exception as e:
      self.fail(f"Error checking PyTorch GPU: {e}")

  def test_filesystem_access(self):
    """Test filesystem read/write access."""
    try:
      with tempfile.NamedTemporaryFile(mode='w+', delete=False) as f:
        f.write("test")
        temp_path = f.name

      with open(temp_path, 'r') as f:
        content = f.read()

      self.assertEqual(content, "test", "File content does not match what was written")

      os.unlink(temp_path)
    except Exception as e:
      self.fail(f"Filesystem access error: {e}")

  def test_project_structure(self):
    """Test that expected project directories exist."""
    expected_dirs = [
      "script_parser",
      "voice_generator",
      "sound_manager",
      "audio_mixer",
      "production_engine",
      "models",
      "ui",
      "utils",
      "tests"
    ]

    # Get the project root directory
    current_dir = Path(__file__).parent
    while current_dir.name != 'audio_drama_generator' and current_dir != current_dir.parent:
      current_dir = current_dir.parent

    # If we didn't find the project root, check the current working directory
    if current_dir == current_dir.parent:
      current_dir = Path.cwd()

    for dir_name in expected_dirs:
      dir_path = current_dir / dir_name
      self.assertTrue(dir_path.exists(), f"Project directory {dir_name} does not exist")
      self.assertTrue(dir_path.is_dir(), f"{dir_name} is not a directory")

if __name__ == "__main__":
  print(f"Python Version: {platform.python_version()}")
  print(f"Platform: {platform.platform()}")
  print(f"Working Directory: {os.getcwd()}")

  # Run all tests
  unittest.main()