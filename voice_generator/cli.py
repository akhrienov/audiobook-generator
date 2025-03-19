#!/usr/bin/env python3
"""
Command-line interface for testing voice generation.

This script provides a CLI for generating test voice samples with different parameters.
"""

import os
import sys
import json
import argparse
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add parent directory to path to import project modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.config_loader import load_config
from voice_generator.voice_generator import (
  initialize_voice_models,
  generate_voice_clip,
  apply_voice_effect
)
from voice_generator.voice_profiles import (
  create_voice_profile,
  generate_character_voice_profile
)

# Setup logging
logging.basicConfig(
  level=logging.INFO,
  format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def generate_character_sample(character_name: str, traits: List[str], text: str,
                              output_dir: str, config: Dict[str, Any]) -> str:
  """
  Generate a voice sample for a character with specified traits.

  Args:
      character_name: Name of the character
      traits: List of voice traits
      text: Text to speak
      output_dir: Output directory
      config: Configuration dictionary

  Returns:
      Path to the generated audio file
  """
  # Create voice profile from traits
  voice_profile = generate_character_voice_profile(traits)

  # Ensure output directory exists
  Path(output_dir).mkdir(parents=True, exist_ok=True)

  # Define output paths
  audio_path = os.path.join(output_dir, f"{character_name.lower()}.wav")
  profile_path = os.path.join(output_dir, f"{character_name.lower()}_profile.json")

  # Save the voice profile
  with open(profile_path, 'w') as f:
    json.dump(voice_profile, f, indent=2)

  # Generate voice sample
  voice_gen = initialize_voice_models(config)
  voice_gen.generate_voice_clip(text, voice_profile, output_path=audio_path)

  logger.info(f"Generated voice sample for {character_name}: {audio_path}")
  logger.info(f"Voice profile saved to: {profile_path}")

  return audio_path


def process_script_file(script_path: str, output_dir: str, config: Dict[str, Any]) -> Dict[str, str]:
  """
  Process a script file and generate voice samples for all characters.

  Args:
      script_path: Path to the script file (JSON or MD)
      output_dir: Output directory
      config: Configuration dictionary

  Returns:
      Dictionary mapping character names to audio file paths
  """
  from script_parser import parse_script, parse_script_safe

  # Parse the script
  script_ext = Path(script_path).suffix.lower()
  try:
    if script_ext == '.json':
      # Load JSON script
      with open(script_path, 'r') as f:
        script_data = json.load(f)
    else:
      # Parse markdown script
      success, result = parse_script_safe(script_path)
      if not success:
        logger.error(f"Failed to parse script: {result}")
        return {}
      script_data = result
  except Exception as e:
    logger.error(f"Error processing script file: {str(e)}")
    return {}

  # Initialize voice generator
  voice_gen = initialize_voice_models(config)

  # Generate voices for all characters
  result = {}

  # Ensure output directory exists
  Path(output_dir).mkdir(parents=True, exist_ok=True)

  for char_code, char_data in script_data.get("characters", {}).items():
    logger.info(f"Generating voice for character: {char_code}")

    # Extract voice traits
    voice_traits = char_data.get("voice_traits", [])

    if not voice_traits:
      logger.warning(f"No voice traits specified for character {char_code}")
      continue

    # Generate voice profile
    try:
      voice_profile = generate_character_voice_profile(voice_traits)

      # Find a sample line from the script for this character
      sample_text = find_character_line(script_data, char_code)
      if not sample_text:
        sample_text = f"My name is {char_code}. This is a sample of my voice."

      # Generate and save voice profile
      profile_path = os.path.join(output_dir, f"{char_code.lower()}_profile.json")
      with open(profile_path, 'w') as f:
        json.dump(voice_profile, f, indent=2)

      # Generate voice sample
      audio_path = os.path.join(output_dir, f"{char_code.lower()}.wav")
      voice_gen.generate_voice_clip(sample_text, voice_profile, output_path=audio_path)

      result[char_code] = audio_path
      logger.info(f"Generated voice sample for {char_code}: {audio_path}")

    except Exception as e:
      logger.error(f"Error generating voice for character {char_code}: {str(e)}")

  return result


def find_character_line(script_data: Dict[str, Any], character_code: str) -> Optional[str]:
  """
  Find a sample dialogue line for a character from the script.

  Args:
      script_data: Parsed script data
      character_code: Character code to find a line for

  Returns:
      A sample dialogue line, or None if not found
  """
  # Look through all scenes and dialogue elements
  for scene in script_data.get("scenes", []):
    for element in scene.get("elements", []):
      if element.get("type") == "dialogue" and element.get("character") == character_code:
        return element.get("text", "")

  return None


def test_voice_effect(audio_path: str, effect_type: str, params: Dict[str, Any], output_dir: str) -> str:
  """
  Test an audio effect on a voice sample.

  Args:
      audio_path: Path to input audio file
      effect_type: Type of effect to apply
      params: Effect parameters
      output_dir: Output directory

  Returns:
      Path to the processed audio file
  """
  # Ensure output directory exists
  Path(output_dir).mkdir(parents=True, exist_ok=True)

  # Define output path
  param_str = "_".join(f"{k}_{v}" for k, v in params.items())
  output_filename = f"{Path(audio_path).stem}_{effect_type}_{param_str}.wav"
  output_path = os.path.join(output_dir, output_filename)

  # Apply effect
  apply_voice_effect(audio_path, effect_type, params, output_path)

  logger.info(f"Applied {effect_type} effect: {output_path}")

  return output_path


def main():
  """Main entry point for the voice generation CLI."""
  parser = argparse.ArgumentParser(description="Voice Generator CLI")
  subparsers = parser.add_subparsers(dest="command", help="Command to execute")

  # Generate a character voice sample
  generate_parser = subparsers.add_parser("generate", help="Generate a voice sample")
  generate_parser.add_argument("--name", "-n", required=True, help="Character name")
  generate_parser.add_argument("--traits", "-t", required=True, nargs="+", help="Voice traits")
  generate_parser.add_argument("--text", "-x", default="This is a sample of my voice.", help="Text to speak")
  generate_parser.add_argument("--output-dir", "-o", default="outputs/voices", help="Output directory")
  generate_parser.add_argument("--config", "-c", help="Path to configuration file")

  # Process a script file
  script_parser = subparsers.add_parser("script", help="Process a script file")
  script_parser.add_argument("script_path", help="Path to script file (JSON or MD)")
  script_parser.add_argument("--output-dir", "-o", default="outputs/voices", help="Output directory")
  script_parser.add_argument("--config", "-c", help="Path to configuration file")

  # Test voice effects
  effect_parser = subparsers.add_parser("effect", help="Test a voice effect")
  effect_parser.add_argument("audio_path", help="Path to input audio file")
  effect_parser.add_argument("--effect", "-e", required=True,
                             choices=["reverb", "echo", "pitch_shift", "timestretch",
                                      "distortion", "tremolo", "lowpass", "highpass", "bandpass",
                                      "eq", "compressor", "noise"],
                             help="Effect type")
  effect_parser.add_argument("--params", "-p", nargs="+", help="Effect parameters in key=value format")
  effect_parser.add_argument("--output-dir", "-o", default="outputs/effects", help="Output directory")

  # List available voice traits
  traits_parser = subparsers.add_parser("list-traits", help="List available voice traits")

  args = parser.parse_args()

  # Load configuration
  config_path = args.config if hasattr(args, "config") and args.config else None
  config = load_config(config_path)

  if args.command == "generate":
    generate_character_sample(
      args.name,
      args.traits,
      args.text,
      args.output_dir,
      config
    )

  elif args.command == "script":
    process_script_file(
      args.script_path,
      args.output_dir,
      config
    )

  elif args.command == "effect":
    # Parse effect parameters
    params = {}
    if args.params:
      for param in args.params:
        key, value = param.split("=", 1)
        try:
          # Try to convert to appropriate type
          if value.lower() == "true":
            params[key] = True
          elif value.lower() == "false":
            params[key] = False
          else:
            try:
              params[key] = float(value)
            except ValueError:
              params[key] = value
        except ValueError:
          params[key] = value

    test_voice_effect(
      args.audio_path,
      args.effect,
      params,
      args.output_dir
    )

  elif args.command == "list-traits":
    # Import here to avoid circular imports
    from voice_generator.voice_profiles import VOICE_TRAIT_MAPPINGS

    print("Available Voice Traits:")
    print("======================")

    # Organize traits by category
    categories = {
      "Pitch": ["deep", "low", "baritone", "bass", "mid-range", "medium", "high", "higher", "soprano"],
      "Speed": ["slow", "deliberate", "measured", "normal", "fast", "fast-talking", "rapid"],
      "Tone Quality": ["gravelly", "rough", "smooth", "raspy", "breathy", "warm", "bright", "dark", "resonant", "melodic", "monotone"],
      "Character": ["confident", "nervous", "shy", "authoritative", "friendly", "threatening", "gentle", "harsh", "sarcastic"],
      "Emotion": ["jovial", "serious", "anxious", "sad", "happy", "angry", "cheerful", "depressed", "excited", "bored"],
      "Age": ["child", "young", "teenage", "middle-aged", "old", "elderly", "ancient"],
      "Accent": ["rural", "urban", "southern", "northern", "western", "eastern", "british", "american", "city-accent", "country-accent", "local-accent"],
      "Modification": ["whispering", "shouting", "nasal", "hoarse", "trembling", "robotic", "distant", "close", "ethereal"],
      "Special": ["narrator", "seductive", "commanding", "timid", "stuttering", "mysterious", "ominous", "frightened", "wise"]
    }

    # Print traits by category
    for category, traits in categories.items():
      print(f"\n{category}:")
      for trait in traits:
        if trait in VOICE_TRAIT_MAPPINGS:
          print(f"  - {trait}")

    print("\nUsage example:")
    print('  python -m voice_generator.cli generate -n "Thomas" -t deep gravelly middle-aged rural')

  else:
    parser.print_help()

  return 0


if __name__ == "__main__":
  sys.exit(main())