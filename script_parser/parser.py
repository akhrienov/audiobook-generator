#!/usr/bin/env python3
"""
Script Parser for the Automated Audio Drama Generator.

This module parses audio drama scripts formatted according to the specification
and extracts structured information for further processing.
"""

import os
import re
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

# Set up logging
logging.basicConfig(
  level=logging.INFO,
  format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ScriptParser:
  """Parser for formatted audio drama scripts."""

  def __init__(self):
    """Initialize the script parser with pattern definitions."""
    # Regex patterns for parsing script elements
    self.patterns = {
      # Meta section patterns
      'title': re.compile(r'^# (.+)$', re.MULTILINE),
      'meta_section': re.compile(r'^## META$.*?(?=^##|\Z)', re.MULTILINE | re.DOTALL),
      'meta_title': re.compile(r'^TITLE: (.+)$', re.MULTILINE),
      'meta_runtime': re.compile(r'^RUNTIME: (.+)$', re.MULTILINE),
      'meta_premise': re.compile(r'^PREMISE: (.+)$', re.MULTILINE),

      # Voice definitions section
      'voices_section': re.compile(r'^## VOICES$.*?(?=^##|\Z)', re.MULTILINE | re.DOTALL),
      'voice_def': re.compile(r'^([A-Z]+): (.+)$', re.MULTILINE),

      # Effects definitions section
      'effects_section': re.compile(r'^## EFFECTS$.*?(?=^##|\Z)', re.MULTILINE | re.DOTALL),
      'effect_def': re.compile(r'^([A-Z]+): (.+)$', re.MULTILINE),

      # Scene patterns
      'scene': re.compile(r'^## SCENE:([A-Z_]+)$(.*?)(?=^## SCENE:|^##|\Z)', re.MULTILINE | re.DOTALL),

      # Scene element patterns
      'dialogue': re.compile(r'^([A-Z]+)(?:\|([a-zA-Z-]+))?: (.+)$', re.MULTILINE),
      'sfx': re.compile(r'^\[SFX\] (.+)$', re.MULTILINE),
      'ambient': re.compile(r'^\[AMBIENT\] (.+)$', re.MULTILINE),
      'music': re.compile(r'^\[MUSIC\] (.+)$', re.MULTILINE),
      'transition': re.compile(r'^\[TRANSITION\] (.+)$', re.MULTILINE)
    }

  def parse_script(self, script_path: str) -> Dict[str, Any]:
    """
    Parse a script file into structured data.

    Args:
        script_path: Path to the script file

    Returns:
        Dictionary containing structured script data
    """
    script_path = Path(script_path)
    logger.info(f"Parsing script: {script_path}")

    try:
      # Read the script file
      with open(script_path, 'r', encoding='utf-8') as f:
        content = f.read()

      # Parse the script
      script_data = self._parse_content(content)

      logger.info(f"Successfully parsed script: {script_path}")
      return script_data

    except Exception as e:
      logger.error(f"Error parsing script {script_path}: {str(e)}")
      raise

  def _parse_content(self, content: str) -> Dict[str, Any]:
    """
    Parse the script content into structured data.

    Args:
        content: Raw script content

    Returns:
        Dictionary containing structured script data
    """
    # Initialize result structure
    script_data = {
      'metadata': {},
      'characters': {},
      'effects': {},
      'scenes': []
    }

    # Parse script title
    title_match = self.patterns['title'].search(content)
    if title_match:
      script_data['metadata']['main_title'] = title_match.group(1).strip()

    # Parse metadata section
    self._parse_metadata(content, script_data)

    # Parse voices section
    self._parse_voices(content, script_data)

    # Parse effects section
    self._parse_effects(content, script_data)

    # Parse scenes
    self._parse_scenes(content, script_data)

    # Validate the parsed data
    self._validate_script_data(script_data)

    return script_data

  def _parse_metadata(self, content: str, script_data: Dict[str, Any]) -> None:
    """
    Parse the metadata section.

    Args:
        content: Raw script content
        script_data: Dictionary to store parsed data
    """
    meta_section_match = self.patterns['meta_section'].search(content)
    if not meta_section_match:
      logger.warning("No META section found in script")
      return

    meta_section = meta_section_match.group(0)

    # Extract title
    title_match = self.patterns['meta_title'].search(meta_section)
    if title_match:
      script_data['metadata']['title'] = title_match.group(1).strip()

    # Extract runtime
    runtime_match = self.patterns['meta_runtime'].search(meta_section)
    if runtime_match:
      script_data['metadata']['runtime'] = runtime_match.group(1).strip()

    # Extract premise
    premise_match = self.patterns['meta_premise'].search(meta_section)
    if premise_match:
      script_data['metadata']['premise'] = premise_match.group(1).strip()

  def _parse_voices(self, content: str, script_data: Dict[str, Any]) -> None:
    """
    Parse the voices section.

    Args:
        content: Raw script content
        script_data: Dictionary to store parsed data
    """
    voices_section_match = self.patterns['voices_section'].search(content)
    if not voices_section_match:
      logger.warning("No VOICES section found in script")
      return

    voices_section = voices_section_match.group(0)

    # Extract voice definitions
    for match in self.patterns['voice_def'].finditer(voices_section):
      character_code = match.group(1).strip()
      traits_str = match.group(2).strip()

      # Parse voice traits (separated by pipes)
      traits = [trait.strip() for trait in traits_str.split('|')]

      script_data['characters'][character_code] = {
        'voice_traits': traits
      }

  def _parse_effects(self, content: str, script_data: Dict[str, Any]) -> None:
    """
    Parse the effects section.

    Args:
        content: Raw script content
        script_data: Dictionary to store parsed data
    """
    effects_section_match = self.patterns['effects_section'].search(content)
    if not effects_section_match:
      logger.warning("No EFFECTS section found in script")
      return

    effects_section = effects_section_match.group(0)

    # Extract effect definitions
    for match in self.patterns['effect_def'].finditer(effects_section):
      effect_name = match.group(1).strip()
      traits_str = match.group(2).strip()

      # Parse effect traits (separated by pipes)
      traits = [trait.strip() for trait in traits_str.split('|')]

      script_data['effects'][effect_name] = traits

  def _parse_scenes(self, content: str, script_data: Dict[str, Any]) -> None:
    """
    Parse the scenes.

    Args:
        content: Raw script content
        script_data: Dictionary to store parsed data
    """
    # Extract scenes
    for match in self.patterns['scene'].finditer(content):
      scene_name = match.group(1).strip()
      scene_content = match.group(2).strip()

      # Parse scene elements
      elements = self._parse_scene_elements(scene_content)

      # Add scene to script data
      script_data['scenes'].append({
        'name': scene_name,
        'elements': elements
      })

  def _parse_scene_elements(self, scene_content: str) -> List[Dict[str, Any]]:
    """
    Parse the elements within a scene.

    Args:
        scene_content: Content of the scene

    Returns:
        List of scene elements (dialogue, sound cues, etc.)
    """
    elements = []

    # Split scene content into lines
    lines = scene_content.strip().split('\n')

    for line in lines:
      line = line.strip()
      if not line:
        continue

      # Check for different types of elements
      element = self._parse_line(line)
      if element:
        elements.append(element)

    return elements

  def _parse_line(self, line: str) -> Optional[Dict[str, Any]]:
    """
    Parse a single line from the script.

    Args:
        line: A line of script content

    Returns:
        Dictionary representing the parsed element, or None if not recognized
    """
    # Check if line is dialogue
    dialogue_match = self.patterns['dialogue'].match(line)
    if dialogue_match:
      character = dialogue_match.group(1)
      modifier = dialogue_match.group(2)
      text = dialogue_match.group(3)

      element = {
        'type': 'dialogue',
        'character': character,
        'text': text
      }

      if modifier:
        # Check if modifier is an EFFECT (all caps) or an emotion (lowercase)
        if modifier.isupper():
          element['effect'] = modifier
        else:
          element['modifier'] = modifier

      return element

    # Check if line is a sound effect
    sfx_match = self.patterns['sfx'].match(line)
    if sfx_match:
      return {
        'type': 'sound',
        'subtype': 'sfx',
        'description': sfx_match.group(1).strip()
      }

    # Check if line is an ambient sound
    ambient_match = self.patterns['ambient'].match(line)
    if ambient_match:
      return {
        'type': 'sound',
        'subtype': 'ambient',
        'description': ambient_match.group(1).strip()
      }

    # Check if line is music
    music_match = self.patterns['music'].match(line)
    if music_match:
      return {
        'type': 'sound',
        'subtype': 'music',
        'description': music_match.group(1).strip()
      }

    # Check if line is a transition
    transition_match = self.patterns['transition'].match(line)
    if transition_match:
      return {
        'type': 'transition',
        'description': transition_match.group(1).strip()
      }

    # If we get here, the line format wasn't recognized
    logger.warning(f"Unrecognized line format: '{line}'")
    return None

  def _validate_script_data(self, script_data: Dict[str, Any]) -> None:
    """
    Validate the parsed script data.

    Args:
        script_data: Dictionary containing parsed script data

    Raises:
        ValueError: If validation fails
    """
    # Check required metadata
    if not script_data['metadata'].get('title'):
      logger.warning("Script is missing title in metadata")

    if not script_data['metadata'].get('premise'):
      logger.warning("Script is missing premise in metadata")

    # Check for characters
    if not script_data['characters']:
      logger.warning("Script has no character definitions")

    # Check for scenes
    if not script_data['scenes']:
      logger.warning("Script has no scenes")

    # Check character references in dialogue
    character_codes = set(script_data['characters'].keys())
    effect_codes = set(script_data['effects'].keys())

    # Check dialogue references
    for scene in script_data['scenes']:
      for element in scene['elements']:
        if element['type'] == 'dialogue':
          character = element['character']
          if character not in character_codes:
            logger.warning(f"Dialogue references undefined character: {character}")

          if 'effect' in element and element['effect'] not in effect_codes:
            logger.warning(f"Dialogue references undefined effect: {element['effect']}")


def parse_script(script_path: str) -> Dict[str, Any]:
  """
  Parse a script file into structured data.

  Args:
      script_path: Path to the script file

  Returns:
      Dictionary containing structured script data
  """
  parser = ScriptParser()
  return parser.parse_script(script_path)


def save_parsed_script(script_data: Dict[str, Any], output_path: str) -> None:
  """
  Save parsed script data to a JSON file.

  Args:
      script_data: Parsed script data
      output_path: Path to save the output
  """
  output_path = Path(output_path)
  output_path.parent.mkdir(parents=True, exist_ok=True)

  with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(script_data, f, indent=2, ensure_ascii=False)

  logger.info(f"Saved parsed script to: {output_path}")


def main():
  """Main entry point."""
  import argparse

  # Set up argument parser
  parser = argparse.ArgumentParser(description="Parse audio drama scripts")
  parser.add_argument("script_path", help="Path to the script file")
  parser.add_argument("--output", "-o", help="Path to save the parsed output (JSON)", default=None)
  parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")

  args = parser.parse_args()

  # Configure logging level
  if args.verbose:
    logging.getLogger().setLevel(logging.DEBUG)

  try:
    # Parse the script
    script_data = parse_script(args.script_path)

    # Determine output path
    if args.output:
      output_path = args.output
    else:
      script_path = Path(args.script_path)
      output_path = script_path.with_suffix('.json')

    # Save the parsed data
    save_parsed_script(script_data, output_path)

    print(f"Script parsed successfully. Output saved to: {output_path}")
    return 0

  except Exception as e:
    logger.error(f"Error: {e}")
    return 1


if __name__ == "__main__":
  import sys
  sys.exit(main())