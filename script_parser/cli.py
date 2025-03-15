#!/usr/bin/env python3
"""
Command Line Interface for the Script Parser.

This script provides a command line interface for parsing audio drama scripts
and generating structured output.
"""

import os
import sys
import json
import logging
import argparse
from pathlib import Path

# Add parent directory to path if running as script
script_dir = Path(__file__).parent.parent
if script_dir not in sys.path:
  sys.path.insert(0, str(script_dir))

from script_parser import ScriptParser
from utils.config_loader import load_config

# Setup logging
logging.basicConfig(
  level=logging.INFO,
  format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
  handlers=[
    logging.StreamHandler(sys.stdout)
  ]
)

logger = logging.getLogger(__name__)

def setup_arg_parser():
  """Set up command line argument parser."""
  parser = argparse.ArgumentParser(
    description='Parse audio drama script files into structured format.'
  )
  parser.add_argument(
    '--script', '-s',
    type=str,
    required=True,
    help='Path to the markdown script file.'
  )
  parser.add_argument(
    '--output', '-o',
    type=str,
    default=None,
    help='Path for the output JSON file. Default: script_path with .json extension.'
  )
  parser.add_argument(
    '--config', '-c',
    type=str,
    default=None,
    help='Path to configuration file. Default: use built-in config.'
  )
  parser.add_argument(
    '--verbose', '-v',
    action='store_true',
    help='Enable verbose output.'
  )
  parser.add_argument(
    '--pretty', '-p',
    action='store_true',
    help='Format JSON output with indentation for readability.'
  )
  parser.add_argument(
    '--validate', '-V',
    action='store_true',
    help='Validate script structure only, without writing output.'
  )
  return parser

def main():
  """Run the script parser CLI."""
  parser = setup_arg_parser()
  args = parser.parse_args()

  # Configure logging level
  if args.verbose:
    logging.getLogger().setLevel(logging.DEBUG)
    logger.debug("Verbose output enabled")

  # Validate input file
  script_path = Path(args.script)
  if not script_path.exists():
    logger.error(f"Script file not found: {script_path}")
    return 1

  # Determine output path if not provided
  if args.output is None and not args.validate:
    args.output = script_path.with_suffix('.json')

  # Load configuration
  config = None
  if args.config:
    try:
      config = load_config(args.config)
      logger.info(f"Loaded configuration from {args.config}")
    except Exception as e:
      logger.error(f"Error loading configuration: {e}")
      return 1

  # Parse the script
  try:
    parser = ScriptParser(config)
    script_structure = parser.parse_script(script_path)

    logger.info(f"Successfully parsed script: {script_path}")
    logger.info(f"Title: {script_structure['metadata'].get('title', 'Untitled')}")
    logger.info(f"Characters: {len(script_structure['characters'])}")
    logger.info(f"Scenes: {len(script_structure['timeline'])}")
    logger.info(f"Estimated duration: {script_structure['estimated_duration']:.2f} seconds")

    # If just validating, exit here
    if args.validate:
      logger.info("Script validation successful")
      return 0

    # Write the output file
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
      if args.pretty:
        json.dump(script_structure, f, indent=2, ensure_ascii=False)
      else:
        json.dump(script_structure, f, ensure_ascii=False)

    logger.info(f"Output written to {output_path}")
    return 0

  except Exception as e:
    logger.error(f"Error parsing script: {e}")
    if args.verbose:
      import traceback
      traceback.print_exc()
    return 1

if __name__ == "__main__":
  sys.exit(main())