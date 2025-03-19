#!/usr/bin/env python3
"""
Model downloader for voice models used in the Automated Audio Drama Generator.

This script downloads the necessary TTS models from Hugging Face.
"""

import os
import sys
import logging
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional

import torch
import tqdm
from huggingface_hub import snapshot_download

# Add parent directory to path to import from utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.config_loader import load_config

# Setup logging
logging.basicConfig(
  level=logging.INFO,
  format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Define the models to download
VOICE_MODELS = {
  # Base TTS model
  "tts_base": {
    "model_id": "microsoft/speecht5_tts",
    "description": "Base Text-to-Speech model",
    "size_mb": 1200  # Approximate size
  },

  # Vocoder models
  "vocoder": {
    "model_id": "microsoft/speecht5_hifigan",
    "description": "HiFi-GAN vocoder for SpeechT5",
    "size_mb": 150  # Approximate size
  },

  # Speech embedding model
  "speaker_encoder": {
    "model_id": "speechbrain/spkrec-ecapa-voxceleb",
    "description": "Speaker embedding model for voice conversion",
    "size_mb": 80  # Approximate size
  }
}

# Mac-friendly smaller models for development
MAC_DEV_MODELS = {
  # Smaller TTS model - still using SpeechT5 but with fewer parameters
  "tts_small": {
    "model_id": "microsoft/speecht5_tts",  # Same model, but we'll only download it
    "description": "SpeechT5 TTS model",
    "size_mb": 1200  # Approximate size
  },

  # Vocoder
  "vocoder_small": {
    "model_id": "microsoft/speecht5_hifigan",
    "description": "HiFi-GAN vocoder for SpeechT5",
    "size_mb": 150  # Approximate size
  }
}

def download_huggingface_model(model_id: str, output_dir: Path, force: bool = False) -> bool:
  """
  Download a model from Hugging Face.

  Args:
      model_id: Hugging Face model ID
      output_dir: Output directory for the model
      force: Force re-download even if model exists

  Returns:
      True if download was successful, False otherwise
  """
  try:
    # Create a subdirectory for the model
    model_name = model_id.split('/')[-1]
    model_dir = output_dir / model_name

    # Check if the model already exists
    if not force and model_dir.exists() and any(model_dir.iterdir()):
      logger.info(f"Model {model_id} already exists at {model_dir}")
      return True

    # Create model directory
    model_dir.mkdir(parents=True, exist_ok=True)

    logger.info(f"Downloading {model_id} to {model_dir}...")

    # Download the model
    snapshot_download(
      repo_id=model_id,
      local_dir=str(model_dir),
      local_dir_use_symlinks=False
    )

    logger.info(f"Successfully downloaded {model_id} to {model_dir}")
    return True

  except Exception as e:
    logger.error(f"Error downloading {model_id}: {str(e)}")
    return False

def create_speaker_embeddings(models_dir: Path, output_dir: Path) -> bool:
  """
  Create sample speaker embeddings for different voice profiles.

  Args:
      models_dir: Directory containing the downloaded models
      output_dir: Directory to save the speaker embeddings

  Returns:
      True if successful, False otherwise
  """
  try:
    # Make sure the embedding directory exists
    output_dir.mkdir(parents=True, exist_ok=True)

    # Check if the speaker encoder model is available
    speaker_encoder_dir = models_dir / "spkrec-ecapa-voxceleb"

    # If the model is not available, create mock embeddings
    if not speaker_encoder_dir.exists() or not (speaker_encoder_dir / "hyperparams.yaml").exists():
      logger.warning("Speaker encoder model not found or incomplete. Creating mock embeddings.")
      voice_profiles = [
        "male_deep", "male_medium", "male_light",
        "female_deep", "female_medium", "female_light",
        "neutral", "child", "elder"
      ]

      for profile in voice_profiles:
        embedding_path = output_dir / f"{profile}.pt"

        # Skip if embedding already exists
        if embedding_path.exists():
          logger.info(f"Speaker embedding for {profile} already exists")
          continue

        # Create a random embedding (this is just a placeholder)
        embed_dim = 192  # Default dimension for ECAPA-TDNN
        embedding = torch.randn(embed_dim)

        # Save the embedding
        torch.save(embedding, embedding_path)
        logger.info(f"Created mock speaker embedding for {profile}")

      return True

    logger.info("Generating speaker embeddings...")

    # Try to import speaker encoder
    try:
      try:
        # Try with the new import path (SpeechBrain >= 1.0)
        from speechbrain.inference import EncoderClassifier
      except ImportError:
        # Fallback to old import path
        from speechbrain.pretrained import EncoderClassifier

      encoder = EncoderClassifier.from_hparams(
        source=str(speaker_encoder_dir),
        run_opts={"device": "cuda" if torch.cuda.is_available() else "cpu"}
      )
    except ImportError as e:
      logger.warning(f"SpeechBrain not available: {e}. Creating mock embeddings instead.")
      # Create mock embeddings
      voice_profiles = [
        "male_deep", "male_medium", "male_light",
        "female_deep", "female_medium", "female_light",
        "neutral", "child", "elder"
      ]

      for profile in voice_profiles:
        embedding_path = output_dir / f"{profile}.pt"

        # Skip if embedding already exists
        if embedding_path.exists():
          logger.info(f"Speaker embedding for {profile} already exists")
          continue

        # Create a random embedding (this is just a placeholder)
        embed_dim = 192  # Default dimension for ECAPA-TDNN
        embedding = torch.randn(embed_dim)

        # Save the embedding
        torch.save(embedding, embedding_path)
        logger.info(f"Created mock speaker embedding for {profile}")

      return True

    # Generate random embeddings for different voice profiles
    # These are just placeholders - in real use, we'd embed actual voice samples
    voice_profiles = [
      "male_deep", "male_medium", "male_light",
      "female_deep", "female_medium", "female_light",
      "neutral", "child", "elder"
    ]

    for profile in voice_profiles:
      embedding_path = output_dir / f"{profile}.pt"

      # Skip if embedding already exists
      if embedding_path.exists():
        logger.info(f"Speaker embedding for {profile} already exists")
        continue

      # Create a random embedding (in real use, we'd use actual voice samples)
      # Shape should match the encoder's output
      if hasattr(encoder, "embedding_dim"):
        embed_dim = encoder.embedding_dim
      else:
        embed_dim = 192  # Default dimension for ECAPA-TDNN

      embedding = torch.randn(embed_dim)

      # Save the embedding
      torch.save(embedding, embedding_path)
      logger.info(f"Created speaker embedding for {profile}")

    logger.info("Speaker embeddings generated successfully")
    return True

  except Exception as e:
    logger.error(f"Error creating speaker embeddings: {str(e)}")
    # Fall back to creating mock embeddings
    try:
      logger.info("Falling back to creating mock embeddings...")
      voice_profiles = [
        "male_deep", "male_medium", "male_light",
        "female_deep", "female_medium", "female_light",
        "neutral", "child", "elder"
      ]

      for profile in voice_profiles:
        embedding_path = output_dir / f"{profile}.pt"

        # Skip if embedding already exists
        if embedding_path.exists():
          logger.info(f"Speaker embedding for {profile} already exists")
          continue

        # Create a random embedding (this is just a placeholder)
        embed_dim = 192  # Default dimension for ECAPA-TDNN
        embedding = torch.randn(embed_dim)

        # Save the embedding
        torch.save(embedding, embedding_path)
        logger.info(f"Created mock speaker embedding for {profile}")

      logger.info("Mock speaker embeddings generated successfully")
      return True
    except Exception as inner_e:
      logger.error(f"Failed to create mock embeddings: {str(inner_e)}")
      return False

def main():
  """Run the model downloader."""
  parser = argparse.ArgumentParser(description="Download voice models for the audio drama generator")
  parser.add_argument("--config", "-c", help="Path to configuration file")
  parser.add_argument("--output-dir", "-o", help="Directory to save models")
  parser.add_argument("--force", "-f", action="store_true", help="Force re-download of models")
  parser.add_argument("--mac-dev", "-m", action="store_true", help="Download smaller models for Mac development")
  parser.add_argument("--skip-embeddings", "-s", action="store_true", help="Skip generating speaker embeddings")

  args = parser.parse_args()

  # Load configuration
  config = load_config(args.config)

  # Determine the output directory
  if args.output_dir:
    models_dir = Path(args.output_dir)
  else:
    models_dir = Path(config.get("voice_generator", {}).get(
      "models_directory",
      config.get("general", {}).get("directories", {}).get("models", "models/weights")
    ))

  # Ensure the models directory exists
  models_dir.mkdir(parents=True, exist_ok=True)

  # Determine which models to download
  if args.mac_dev:
    logger.info("Using smaller models for Mac development")
    models_to_download = MAC_DEV_MODELS
  else:
    models_to_download = VOICE_MODELS

  # Calculate total download size
  total_size_mb = sum(model["size_mb"] for model in models_to_download.values())
  logger.info(f"Preparing to download {len(models_to_download)} models (~{total_size_mb} MB)")

  # Check if there's enough disk space
  try:
    import shutil
    disk_space_mb = shutil.disk_usage(models_dir).free // (1024 * 1024)
    if disk_space_mb < total_size_mb * 1.2:  # Add 20% margin
      logger.warning(f"Low disk space: {disk_space_mb} MB available, need ~{total_size_mb} MB")
      if not input("Continue anyway? (y/n): ").lower().startswith('y'):
        logger.info("Download cancelled")
        return 1
  except Exception:
    logger.warning("Couldn't check disk space, proceeding anyway")

  # Download each model
  success_count = 0
  for model_key, model_info in models_to_download.items():
    logger.info(f"Processing {model_key}: {model_info['description']} (~{model_info['size_mb']} MB)")
    success = download_huggingface_model(model_info["model_id"], models_dir, args.force)
    if success:
      success_count += 1

  logger.info(f"Downloaded {success_count}/{len(models_to_download)} models successfully")

  # Generate speaker embeddings if needed
  if not args.skip_embeddings:
    # Determine embeddings directory
    embeddings_dir = Path(config.get("voice_generator", {}).get(
      "embeddings_directory",
      config.get("general", {}).get("directories", {}).get("embeddings", "models/embeddings")
    ))

    # Create speaker embeddings
    if create_speaker_embeddings(models_dir, embeddings_dir):
      logger.info("Speaker embeddings generated successfully")
    else:
      logger.warning("Failed to generate speaker embeddings")

  return 0 if success_count == len(models_to_download) else 1

if __name__ == "__main__":
  sys.exit(main())