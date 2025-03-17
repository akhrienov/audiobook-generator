"""
Script validator for the Automated Audio Drama Generator.

This module validates audio drama scripts against the format specification.
"""

import re
import logging
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path

from .parser import parse_script

logger = logging.getLogger(__name__)

def check_script_format(script_path):
  """
  Check if a script follows the required format.

  Args:
      script_path: Path to the script file

  Returns:
      Tuple of (is_valid, errors)
  """
  try:
    # Read the script
    with open(script_path, 'r', encoding='utf-8') as f:
      content = f.read()

    errors = []

    # Check for required sections
    if not re.search(r'^# ', content, re.MULTILINE):
      errors.append("Missing script title (# TITLE)")

    if not re.search(r'^## META$', content, re.MULTILINE):
      errors.append("Missing META section (## META)")

    if not re.search(r'^## VOICES$', content, re.MULTILINE):
      errors.append("Missing VOICES section (## VOICES)")

    if not re.search(r'^## EFFECTS$', content, re.MULTILINE):
      errors.append("Missing EFFECTS section (## EFFECTS)")

    if not re.search(r'^## SCENE:', content, re.MULTILINE):
      errors.append("Missing scene definitions (## SCENE:NAME)")

    # Check for required metadata
    if not re.search(r'^TITLE:', content, re.MULTILINE):
      errors.append("Missing title in META section (TITLE:)")

    if not re.search(r'^RUNTIME:', content, re.MULTILINE):
      errors.append("Missing runtime in META section (RUNTIME:)")

    if not re.search(r'^PREMISE:', content, re.MULTILINE):
      errors.append("Missing premise in META section (PREMISE:)")

    return len(errors) == 0, errors

  except Exception as e:
    return False, [f"Error checking script format: {str(e)}"]

def validate_script(script_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
  """
  Validate the parsed script data.

  Args:
      script_data: Dictionary containing parsed script data

  Returns:
      Tuple of (is_valid, error_messages)
  """
  errors = []

  # Check required metadata
  if 'metadata' not in script_data:
    errors.append("Script is missing metadata section")
  else:
    metadata = script_data['metadata']
    if 'title' not in metadata:
      errors.append("Script is missing title in metadata")
    if 'runtime' not in metadata:
      errors.append("Script is missing runtime in metadata")
    if 'premise' not in metadata:
      errors.append("Script is missing premise in metadata")

  # Check for characters
  if 'characters' not in script_data or not script_data['characters']:
    errors.append("Script has no character definitions")

  # Check for scenes
  if 'scenes' not in script_data or not script_data['scenes']:
    errors.append("Script has no scenes")

  # Validate character references in dialogue
  if 'characters' in script_data and 'scenes' in script_data:
    character_codes = set(script_data['characters'].keys())

    for scene_idx, scene in enumerate(script_data['scenes']):
      if 'elements' not in scene:
        continue

      for elem_idx, element in enumerate(scene['elements']):
        if element.get('type') == 'dialogue':
          character = element.get('character')
          if character and character not in character_codes:
            errors.append(f"Scene {scene['name']}, element {elem_idx}: "
                          f"References undefined character '{character}'")

  # Validate effect references
  if 'effects' in script_data and 'scenes' in script_data:
    effect_codes = set(script_data['effects'].keys())

    for scene_idx, scene in enumerate(script_data['scenes']):
      if 'elements' not in scene:
        continue

      for elem_idx, element in enumerate(scene['elements']):
        if element.get('type') == 'dialogue' and 'effect' in element:
          effect = element['effect']
          if effect not in effect_codes:
            errors.append(f"Scene {scene['name']}, element {elem_idx}: "
                          f"References undefined effect '{effect}'")

  return len(errors) == 0, errors

def parse_script_safe(script_path):
  """
  Safely parse a script with error handling.

  Args:
      script_path: Path to the script file

  Returns:
      Tuple of (success, result)
      - If success is True, result is the parsed script data
      - If success is False, result is an error message
  """
  try:
    script_data = parse_script(script_path)
    return True, script_data
  except FileNotFoundError:
    return False, f"Script file not found: {script_path}"
  except UnicodeDecodeError:
    return False, f"Script file encoding error: {script_path}"
  except Exception as e:
    return False, f"Error parsing script: {str(e)}"