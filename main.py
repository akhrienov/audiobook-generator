#!/usr/bin/env python3
"""
Main script for generating audio dramas.
"""

import os
import sys
import logging
import argparse
from pathlib import Path

# Import modules
from script_parser import parse_script
# You'll implement these modules next
from voice_generator import generate_voices
from sound_manager import process_sounds
from audio_mixer import mix_audio_drama

# Set up logging
logging.basicConfig(
  level=logging.INFO,
  format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def generate_audio_drama(script_path, output_path=None, config_path=None):
  """
  Generate an audio drama from a script.

  Args:
      script_path: Path to the script file
      output_path: Path for the output audio file
      config_path: Path to configuration file

  Returns:
      Path to the generated audio file
  """
  script_path = Path(script_path)

  # Default output path if not provided
  if output_path is None:
    output_path = script_path.with_suffix('.wav')
  else:
    output_path = Path(output_path)

  # Ensure output directory exists
  output_path.parent.mkdir(parents=True, exist_ok=True)

  logger.info(f"Generating audio drama from script: {script_path}")
  logger.info(f"Output will be saved to: {output_path}")

  # Step 1: Parse the script
  logger.info("Parsing script...")
  script_data = parse_script(script_path)

  # Step 2: Generate voices
  logger.info("Generating character voices...")
  voice_files = generate_voices(script_data)

  # Step 3: Process sound effects
  logger.info("Processing sound effects...")
  sound_files = process_sounds(script_data)

  # Step 4: Mix the audio drama
  logger.info("Mixing audio drama...")
  mix_audio_drama(script_data, voice_files, sound_files, output_path)

  logger.info(f"Audio drama generated successfully: {output_path}")
  return output_path

def main():
  """Main entry point."""
  parser = argparse.ArgumentParser(description="Generate audio drama from script")
  parser.add_argument("script", help="Path to the script file")
  parser.add_argument("--output", "-o", help="Path to the output audio file")
  parser.add_argument("--config", "-c", help="Path to configuration file")
  parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")

  args = parser.parse_args()

  # Set logging level
  if args.verbose:
    logging.getLogger().setLevel(logging.DEBUG)

  try:
    output_path = generate_audio_drama(args.script, args.output, args.config)
    print(f"Audio drama generated: {output_path}")
    return 0
  except Exception as e:
    logger.error(f"Error generating audio drama: {e}")
    return 1

if __name__ == "__main__":
  sys.exit(main())