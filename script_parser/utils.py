"""
Utility functions for the script parser.
"""

import json
import logging
from pathlib import Path

from .parser import parse_script, save_parsed_script
from .validator import check_script_format

logger = logging.getLogger(__name__)

def generate_script_stats(script_data):
  """
  Generate statistics about the script.

  Args:
      script_data: Parsed script data

  Returns:
      Dictionary of statistics
  """
  stats = {
    'title': script_data['metadata'].get('title', 'Untitled'),
    'character_count': len(script_data['characters']),
    'scene_count': len(script_data['scenes']),
    'dialogue_count': 0,
    'sound_count': 0,
    'words_total': 0,
    'estimated_runtime_seconds': 0,
    'characters_dialogue': {},
    'sound_types': {
      'sfx': 0,
      'ambient': 0,
      'music': 0,
      'transition': 0
    }
  }

  # Initialize character dialogue counts
  for char in script_data['characters']:
    stats['characters_dialogue'][char] = {
      'line_count': 0,
      'word_count': 0
    }

  # Process scenes
  for scene in script_data['scenes']:
    for element in scene['elements']:
      if element['type'] == 'dialogue':
        stats['dialogue_count'] += 1
        words = len(element['text'].split())
        stats['words_total'] += words

        # Add to character stats
        char = element['character']
        if char in stats['characters_dialogue']:
          stats['characters_dialogue'][char]['line_count'] += 1
          stats['characters_dialogue'][char]['word_count'] += words

      elif element['type'] == 'sound':
        stats['sound_count'] += 1
        subtype = element.get('subtype', 'unknown')
        if subtype in stats['sound_types']:
          stats['sound_types'][subtype] += 1

      elif element['type'] == 'transition':
        stats['sound_types']['transition'] += 1

  # Estimate runtime (very rough estimate)
  # Assuming average speaking rate of 150 words per minute
  # Add 5 seconds for each sound effect
  # Add extra time for scene transitions
  speaking_time = stats['words_total'] / 150 * 60  # seconds
  sound_time = stats['sound_count'] * 5  # seconds
  transition_time = stats['scene_count'] * 3  # seconds

  stats['estimated_runtime_seconds'] = speaking_time + sound_time + transition_time
  stats['estimated_runtime_minutes'] = stats['estimated_runtime_seconds'] / 60

  return stats

def convert_to_html(script_data, output_path):
  """
  Convert the script to HTML format.

  Args:
      script_data: Parsed script data
      output_path: Path to save the HTML file

  Returns:
      Path to the generated HTML file
  """
  # Create HTML content
  html = ['<!DOCTYPE html>',
          '<html>',
          '<head>',
          f'<title>{script_data["metadata"].get("title", "Audio Drama Script")}</title>',
          '<style>',
          'body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }',
          'h1 { color: #2c3e50; }',
          'h2 { color: #3498db; margin-top: 30px; }',
          '.scene { margin-top: 30px; border-left: 4px solid #3498db; padding-left: 15px; }',
          '.scene-title { font-weight: bold; color: #2980b9; }',
          '.dialogue { margin: 10px 0; }',
          '.character { font-weight: bold; color: #16a085; }',
          '.sound { color: #8e44ad; margin: 5px 0; font-style: italic; }',
          '.transition { color: #c0392b; margin: 5px 0; font-weight: bold; }',
          '.meta-section { background: #f8f9fa; padding: 10px; border-radius: 5px; }',
          '</style>',
          '</head>',
          '<body>']

  # Title and metadata
  html.append(f'<h1>{script_data["metadata"].get("title", "Untitled")}</h1>')
  html.append('<div class="meta-section">')
  html.append(f'<p><strong>Runtime:</strong> {script_data["metadata"].get("runtime", "Not specified")}</p>')
  html.append(f'<p><strong>Premise:</strong> {script_data["metadata"].get("premise", "Not specified")}</p>')
  html.append('</div>')

  # Characters
  html.append('<h2>Characters</h2>')
  html.append('<ul>')
  for char_code, char_data in script_data['characters'].items():
    traits = ', '.join(char_data.get('voice_traits', []))
    html.append(f'<li><strong>{char_code}:</strong> {traits}</li>')
  html.append('</ul>')

  # Effects
  if script_data['effects']:
    html.append('<h2>Effects</h2>')
    html.append('<ul>')
    for effect_name, effect_traits in script_data['effects'].items():
      traits = ', '.join(effect_traits)
      html.append(f'<li><strong>{effect_name}:</strong> {traits}</li>')
    html.append('</ul>')

  # Scenes
  html.append('<h2>Scenes</h2>')
  for scene in script_data['scenes']:
    html.append(f'<div class="scene">')
    html.append(f'<div class="scene-title">SCENE: {scene["name"]}</div>')

    for element in scene['elements']:
      if element['type'] == 'dialogue':
        character = element['character']
        text = element['text']
        modifier = element.get('modifier', '')
        effect = element.get('effect', '')

        modifier_text = f" ({modifier})" if modifier else ""
        effect_text = f" [{effect}]" if effect else ""

        html.append(f'<div class="dialogue">')
        html.append(f'<span class="character">{character}{modifier_text}{effect_text}:</span> {text}')
        html.append(f'</div>')

      elif element['type'] == 'sound':
        subtype = element.get('subtype', 'sound')
        description = element.get('description', '')
        html.append(f'<div class="sound">[{subtype.upper()}] {description}</div>')

      elif element['type'] == 'transition':
        description = element.get('description', '')
        html.append(f'<div class="transition">[TRANSITION] {description}</div>')

    html.append('</div>')

  # Close HTML tags
  html.append('</body>')
  html.append('</html>')

  # Write HTML to file
  output_path = Path(output_path)
  with open(output_path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(html))

  return output_path

def batch_process_scripts(input_dir, output_dir=None, format='json'):
  """
  Process all script files in a directory.

  Args:
      input_dir: Directory containing script files
      output_dir: Directory to save processed files (defaults to input_dir)
      format: Output format ('json', 'html', or 'stats')

  Returns:
      Dictionary with results
  """
  input_dir = Path(input_dir)
  if output_dir is None:
    output_dir = input_dir
  else:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

  results = {
    'success': [],
    'failed': []
  }

  # Find all markdown files
  script_files = list(input_dir.glob('*.md'))

  for script_path in script_files:
    try:
      # Parse the script
      script_data = parse_script(script_path)

      # Generate output based on format
      if format == 'json':
        output_path = output_dir / f"{script_path.stem}.json"
        save_parsed_script(script_data, output_path)

      elif format == 'html':
        output_path = output_dir / f"{script_path.stem}.html"
        convert_to_html(script_data, output_path)

      elif format == 'stats':
        stats = generate_script_stats(script_data)
        output_path = output_dir / f"{script_path.stem}_stats.json"

        with open(output_path, 'w', encoding='utf-8') as f:
          json.dump(stats, f, indent=2)

      results['success'].append(str(script_path))

    except Exception as e:
      results['failed'].append({
        'path': str(script_path),
        'error': str(e)
      })

  return results

def run_integration_test(script_path):
  """
  Run an integration test on the script parser.

  Args:
      script_path: Path to the test script

  Returns:
      True if all tests pass, False otherwise
  """
  print(f"Running integration test on: {script_path}")
  all_passed = True

  # Test 1: Basic parsing
  print("\n=== Test 1: Basic Parsing ===")
  try:
    script_data = parse_script(script_path)
    print("✓ Basic parsing successful")

    # Print basic info
    print(f"  Title: {script_data['metadata'].get('title', 'Untitled')}")
    print(f"  Characters: {len(script_data['characters'])}")
    print(f"  Effects: {len(script_data['effects'])}")
    print(f"  Scenes: {len(script_data['scenes'])}")
  except Exception as e:
    print(f"✗ Basic parsing failed: {e}")
    all_passed = False
    return all_passed  # If basic parsing fails, stop testing

  # Test 2: Format validation
  print("\n=== Test 2: Format Validation ===")
  success, errors = check_script_format(script_path)
  if success:
    print("✓ Format validation passed")
  else:
    print("✗ Format validation failed:")
    for error in errors:
      print(f"  - {error}")
    all_passed = False

  # Test 3: Script statistics
  print("\n=== Test 3: Script Statistics ===")
  try:
    stats = generate_script_stats(script_data)
    print("✓ Statistics generation successful")
    print(f"  Dialogue lines: {stats['dialogue_count']}")
    print(f"  Total words: {stats['words_total']}")
    print(f"  Estimated runtime: {stats['estimated_runtime_minutes']:.1f} minutes")
  except Exception as e:
    print(f"✗ Statistics generation failed: {e}")
    all_passed = False

  # Test 4: HTML conversion
  print("\n=== Test 4: HTML Conversion ===")
  try:
    html_path = Path(script_path).with_suffix('.test.html')
    convert_to_html(script_data, html_path)
    print(f"✓ HTML conversion successful: {html_path}")
  except Exception as e:
    print(f"✗ HTML conversion failed: {e}")
    all_passed = False

  # Test 5: Character validation
  print("\n=== Test 5: Character Validation ===")
  try:
    undefined_chars = set()
    for scene in script_data['scenes']:
      for element in scene['elements']:
        if element['type'] == 'dialogue':
          char = element['character']
          if char not in script_data['characters']:
            undefined_chars.add(char)

    if undefined_chars:
      print(f"✗ Found undefined characters: {', '.join(undefined_chars)}")
      all_passed = False
    else:
      print("✓ All characters properly defined")
  except Exception as e:
    print(f"✗ Character validation failed: {e}")
    all_passed = False

  # Summary
  print("\n=== Test Summary ===")
  if all_passed:
    print("✓ All tests passed successfully!")
  else:
    print("✗ Some tests failed. See details above.")

  return all_passed

def generate_script_visualization(script_data, output_path):
  """
  Generate a visual representation of the script structure.

  Args:
      script_data: Parsed script data
      output_path: Path to save the visualization

  Returns:
      Path to the generated visualization
  """
  try:
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches
    import numpy as np

    # Create figure and axis
    fig, ax = plt.subplots(figsize=(12, 8))

    # Set title
    title = script_data['metadata'].get('title', 'Untitled Script')
    ax.set_title(f"Script Structure: {title}", fontsize=16)

    # Prepare data
    scenes = script_data['scenes']
    scene_names = [scene['name'] for scene in scenes]
    scene_lengths = [len(scene['elements']) for scene in scenes]

    # Set up the plot
    ax.set_xlim(0, max(scene_lengths) + 2)
    ax.set_ylim(0, len(scenes) * 2 + 2)
    ax.set_xlabel('Number of Elements', fontsize=12)
    ax.set_yticks(np.arange(1, len(scenes) * 2 + 1, 2))
    ax.set_yticklabels(scene_names)

    # Plot each scene as a horizontal bar
    colors = {
      'dialogue': 'blue',
      'sound': 'green',
      'transition': 'red'
    }

    for i, scene in enumerate(scenes):
      y_pos = (i * 2) + 1

      # Plot scene background
      ax.add_patch(patches.Rectangle(
        (0, y_pos - 0.5),
        len(scene['elements']),
        1,
        facecolor='lightgray',
        alpha=0.3
      ))

      # Plot each element as a colored square
      for j, element in enumerate(scene['elements']):
        element_type = element['type']
        color = colors.get(element_type, 'gray')

        # Add a small rectangle for each element
        ax.add_patch(patches.Rectangle(
          (j, y_pos - 0.4),
          0.8,
          0.8,
          facecolor=color,
          alpha=0.7
        ))

    # Add legend
    legend_elements = [
      patches.Patch(facecolor='blue', alpha=0.7, label='Dialogue'),
      patches.Patch(facecolor='green', alpha=0.7, label='Sound'),
      patches.Patch(facecolor='red', alpha=0.7, label='Transition')
    ]
    ax.legend(handles=legend_elements, loc='upper right')

    # Save figure
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()

    return output_path

  except ImportError:
    print("Matplotlib and/or numpy not installed. Cannot generate visualization.")
    print("Install with: pip install matplotlib numpy")
    return None