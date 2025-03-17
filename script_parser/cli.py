"""
Command-line interface for the script parser.
"""

import logging
import argparse
import sys
from pathlib import Path

from .parser import parse_script, save_parsed_script
from .validator import check_script_format
from .utils import (
  generate_script_stats,
  generate_script_visualization,
  convert_to_html,
  batch_process_scripts,
  run_integration_test
)

logger = logging.getLogger(__name__)

def main():
  """Main entry point with enhanced CLI."""
  print("Script parser CLI started")  # Debug print to confirm execution

  parser = argparse.ArgumentParser(description="Audio Drama Script Parser")

  # Create subparsers for different commands
  subparsers = parser.add_subparsers(dest='command', help='Command to execute')

  # Parse command
  parse_parser = subparsers.add_parser('parse', help='Parse a script file')
  parse_parser.add_argument('script_path', help='Path to the script file')
  parse_parser.add_argument('--output', '-o', help='Path to save the parsed output')
  parse_parser.add_argument('--format', '-f', choices=['json', 'html'], default='json',
                            help='Output format (default: json)')

  # Validate command
  validate_parser = subparsers.add_parser('validate', help='Validate a script file')
  validate_parser.add_argument('script_path', help='Path to the script file')

  # Stats command
  stats_parser = subparsers.add_parser('stats', help='Generate script statistics')
  stats_parser.add_argument('script_path', help='Path to the script file')
  stats_parser.add_argument('--output', '-o', help='Path to save the statistics')

  # Batch command
  batch_parser = subparsers.add_parser('batch', help='Batch process multiple scripts')
  batch_parser.add_argument('input_dir', help='Directory containing script files')
  batch_parser.add_argument('--output', '-o', help='Directory to save processed files')
  batch_parser.add_argument('--format', '-f', choices=['json', 'html', 'stats'], default='json',
                            help='Output format (default: json)')

  # Visualization command
  viz_parser = subparsers.add_parser('visualize', help='Generate script visualization')
  viz_parser.add_argument('script_path', help='Path to the script file')
  viz_parser.add_argument('--output', '-o', help='Path to save the visualization')

  # Test command
  test_parser = subparsers.add_parser('test', help='Run integration test on a script')
  test_parser.add_argument('script_path', help='Path to the script file')

  # Global options
  parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose output')
  parser.add_argument('--debug', action='store_true', help='Enable debug output')

  args = parser.parse_args()

  # Enable debug output
  if args.debug:
    print(f"Debug: Command selected: {args.command}")
    print(f"Debug: Arguments: {args}")

  # Set up logging
  if args.verbose:
    logging.getLogger().setLevel(logging.DEBUG)

  # Execute the appropriate command
  if args.command == 'parse':
    try:
      print(f"Parsing script: {args.script_path}")
      script_data = parse_script(args.script_path)

      if args.format == 'json':
        output_path = args.output or Path(args.script_path).with_suffix('.json')
        save_parsed_script(script_data, output_path)
      else:  # html
        output_path = args.output or Path(args.script_path).with_suffix('.html')
        convert_to_html(script_data, output_path)

      print(f"Script parsed successfully. Output saved to: {output_path}")
      return 0
    except Exception as e:
      print(f"Error parsing script: {e}")
      return 1

  elif args.command == 'validate':
    print(f"Validating script: {args.script_path}")
    success, errors = check_script_format(args.script_path)
    if success:
      print(f"✅ Script is valid: {args.script_path}")
      return 0
    else:
      print(f"❌ Script validation failed for: {args.script_path}")
      for i, error in enumerate(errors, 1):
        print(f"  {i}. {error}")
      return 1

  elif args.command == 'stats':
    try:
      print(f"Generating statistics for: {args.script_path}")
      script_data = parse_script(args.script_path)
      stats = generate_script_stats(script_data)

      script_path = Path(args.script_path)
      output_path = args.output or (script_path.parent / f"{script_path.stem}_stats.json")
      with open(output_path, 'w', encoding='utf-8') as f:
        import json
        json.dump(stats, f, indent=2)

      # Print summary
      print(f"Script: {stats['title']}")
      print(f"Characters: {stats['character_count']}")
      print(f"Scenes: {stats['scene_count']}")
      print(f"Dialogue lines: {stats['dialogue_count']}")
      print(f"Sound effects: {stats['sound_count']}")
      print(f"Total words: {stats['words_total']}")
      print(f"Estimated runtime: {stats['estimated_runtime_minutes']:.1f} minutes")
      print(f"Full statistics saved to: {output_path}")
      return 0
    except Exception as e:
      print(f"Error generating statistics: {e}")
      return 1

  elif args.command == 'batch':
    print(f"Batch processing scripts in: {args.input_dir}")
    results = batch_process_scripts(args.input_dir, args.output, args.format)
    print(f"Batch processing complete. Processed {len(results['success'])} files successfully.")
    if results['failed']:
      print(f"Failed to process {len(results['failed'])} files:")
      for fail in results['failed']:
        print(f"  {fail['path']}: {fail['error']}")
    return 0

  elif args.command == 'visualize':
    try:
      print(f"Generating visualization for: {args.script_path}")
      script_data = parse_script(args.script_path)
      output_path = args.output or Path(args.script_path).with_suffix('.png')

      viz_path = generate_script_visualization(script_data, output_path)
      if viz_path:
        print(f"Visualization saved to: {viz_path}")
        return 0
      else:
        print("Failed to generate visualization.")
        return 1
    except Exception as e:
      print(f"Error generating visualization: {e}")
      return 1

  elif args.command == 'test':
    print(f"Running integration test on: {args.script_path}")
    success = run_integration_test(args.script_path)
    return 0 if success else 1

  else:
    print("No command specified")
    parser.print_help()
    return 1

# This is critically important - make sure it's here
if __name__ == "__main__":
  sys.exit(main())