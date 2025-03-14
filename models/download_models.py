#!/usr/bin/env python3
"""
Model downloader for the Automated Audio Drama Generator.

This script downloads the necessary models from Hugging Face.
"""

import os
import sys
import logging
import argparse
from pathlib import Path
from tqdm import tqdm
import huggingface_hub

# Setup logging
logging.basicConfig(
  level=logging.INFO,
  format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
  handlers=[
    logging.StreamHandler(sys.stdout)
  ]
)

logger = logging.getLogger(__name__)

# Define the models to download
MODELS = {
  "tts": {
    "model_id": "microsoft/speecht5_tts",
    "description": "Base TTS model for voice generation"
  },
  "voice_conversion": {
    "model_id": "facebook/fastspeech2-en-ljspeech",
    "description": "Model for voice conversion and characteristics"
  },
  "vocoder": {
    "model_id": "facebook/vits-ljspeech",
    "description": "Vocoder model for high-quality speech synthesis"
  },
  "embedder": {
    "model_id": "speechbrain/spkrec-ecapa-voxceleb",
    "description": "Speaker embedding model for voice characteristics"
  },
  "audio_classification": {
    "model_id": "MIT/ast-fsd50k",
    "description": "Audio classification model for sound effects"
  }
}

def setup_arg_parser():
  """Set up command line argument parser."""
  parser = argparse.ArgumentParser(
    description='Download models for the audio drama generator.'
  )
  parser.add_argument(
    '--model-dir', '-d',
    type=str,
    default=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models', 'weights'),
    help='Directory to save models. Default: ./models/weights'
  )
  parser.add_argument(
    '--models', '-m',
    type=str,
    nargs='+',
    choices=list(MODELS.keys()) + ['all'],
    default=['all'],
    help='Models to download. Default: all'
  )
  parser.add_argument(
    '--force', '-f',
    action='store_true',
    help='Force re-download even if models exist.'
  )
  return parser

def download_model(model_id, output_dir, force=False):
  """
  Download a model from Hugging Face.

  Args:
      model_id (str): Hugging Face model ID
      output_dir (Path): Output directory
      force (bool): Force re-download even if files exist

  Returns:
      bool: True if download was successful
  """
  try:
    # Create a subdirectory for the model
    model_name = model_id.split('/')[-1]
    model_dir = output_dir / model_name
    model_dir.mkdir(parents=True, exist_ok=True)

    # Check if already downloaded
    if not force and any(model_dir.iterdir()):
      logger.info(f"Model {model_id} already exists. Use --force to re-download.")
      return True

    logger.info(f"Downloading {model_id}...")

    # Using snapshot_download to get the complete model with all files
    huggingface_hub.snapshot_download(
      repo_id=model_id,
      local_dir=str(model_dir),
      use_auth_token=False
    )

    logger.info(f"Successfully downloaded {model_id} to {model_dir}")
    return True

  except Exception as e:
    logger.error(f"Error downloading {model_id}: {e}")
    return False

def main():
  """Run the model downloader."""
  parser = setup_arg_parser()
  args = parser.parse_args()

  # Create output directory
  output_dir = Path(args.model_dir)
  output_dir.mkdir(parents=True, exist_ok=True)

  logger.info(f"Downloading models to {output_dir}")

  # Determine which models to download
  models_to_download = MODELS.keys() if 'all' in args.models else args.models

  # Download each model
  success_count = 0
  for model_key in models_to_download:
    model_info = MODELS[model_key]
    logger.info(f"Processing {model_key}: {model_info['description']}")

    if download_model(model_info['model_id'], output_dir, args.force):
      success_count += 1

  # Report results
  total_models = len(models_to_download)
  logger.info(f"Downloaded {success_count}/{total_models} models successfully")

  if success_count < total_models:
    logger.warning("Some models failed to download. Check logs for details.")
    return 1

  logger.info("All models downloaded successfully!")
  return 0

if __name__ == "__main__":
  sys.exit(main())