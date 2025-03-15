#!/usr/bin/env python3
"""
Script Structure Builder for the Automated Audio Drama Generator.

This module transforms the extracted script elements into a unified structure
with proper timing relationships and sequence information.
"""

import logging
from pathlib import Path
import json
from typing import Dict, List, Any, Optional, Tuple

# Setup logging
logger = logging.getLogger(__name__)

class ScriptStructureBuilder:
  """Builds a unified script structure from parsed elements."""

  def __init__(self, config=None):
    """
    Initialize the script structure builder.

    Args:
        config (dict, optional): Configuration options
    """
    self.config = config or {}

    # Default parameters
    self.params = {
      'words_per_minute': 150,  # Average speaking rate
      'pause_after_sound': 0.5,  # Seconds to pause after a sound
      'pause_between_speakers': 0.3,  # Seconds to pause between speakers
      'pause_after_scene': 1.5,  # Seconds to pause after a scene
      'average_sound_duration': 3.0,  # Default duration for sound effects
    }

    # Override with config if provided
    if config and 'script_parser' in config and 'timing' in config['script_parser']:
      self.params.update(config['script_parser']['timing'])

  def build_script_structure(self,
                             metadata: Dict[str, str],
                             characters: Dict[str, Dict[str, Any]],
                             scenes: List[Dict[str, Any]],
                             sound_cues: List[Dict[str, Any]],
                             special_treatments: List[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Build a unified script structure with timing relationships.

    Args:
        metadata (dict): Script metadata
        characters (dict): Character information
        scenes (list): Scene information
        sound_cues (list): Sound cues
        special_treatments (list, optional): Special sound treatments

    Returns:
        dict: Unified script structure
    """
    if special_treatments is None:
      special_treatments = []

    # Create the base structure
    script_structure = {
      'metadata': metadata,
      'characters': characters,
      'timeline': [],
      'special_treatments': special_treatments,
      'estimated_duration': 0
    }

    # Build a timeline of all elements with timing information
    current_time = 0.0

    for scene in scenes:
      scene_start_time = current_time
      scene_elements = []

      # Process each element in the scene
      for element in scene['elements']:
        # Add timing information
        element_with_timing = element.copy()
        element_with_timing['start_time'] = current_time

        # Calculate element duration
        duration = self._calculate_element_duration(element, characters)
        element_with_timing['duration'] = duration

        # Add element to the scene timeline
        scene_elements.append(element_with_timing)

        # Update current time
        current_time += duration

        # Add appropriate pause based on element type
        if element['type'] == 'sound':
          current_time += self.params['pause_after_sound']
        elif element['type'] == 'dialogue':
          current_time += self.params['pause_between_speakers']

      # Add scene information to the timeline
      script_structure['timeline'].append({
        'type': 'scene',
        'name': scene['name'],
        'start_time': scene_start_time,
        'end_time': current_time,
        'duration': current_time - scene_start_time,
        'elements': scene_elements
      })

      # Add pause after scene
      current_time += self.params['pause_after_scene']

    # Set the estimated total duration
    script_structure['estimated_duration'] = current_time

    # Add timing information to special treatments
    self._process_special_treatments(script_structure)

    logger.info(f"Built script structure with {len(script_structure['timeline'])} scenes")
    logger.info(f"Estimated duration: {script_structure['estimated_duration']:.2f} seconds")

    # Add additional metadata for production
    minutes, seconds = divmod(script_structure['estimated_duration'], 60)
    script_structure['formatted_duration'] = f"{int(minutes)}:{int(seconds):02d}"
    script_structure['word_count'] = self._count_total_words(script_structure)

    return script_structure

  def _count_total_words(self, script_structure: Dict[str, Any]) -> int:
    """
    Count the total number of spoken words in the script.

    Args:
        script_structure (dict): Script structure

    Returns:
        int: Total word count
    """
    word_count = 0

    for scene in script_structure['timeline']:
      for element in scene['elements']:
        if element['type'] == 'dialogue':
          word_count += len(element['text'].split())

    return word_count

  def save_script_structure(self, script_structure: Dict[str, Any], output_path: str) -> None:
    """
    Save the script structure to a JSON file.

    Args:
        script_structure (dict): Script structure
        output_path (str): Path to save the structure file
    """
    output_path = Path(output_path)

    # Create parent directories if they don't exist
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
      json.dump(script_structure, f, indent=2, ensure_ascii=False)

    logger.info(f"Script structure saved to {output_path}")

  def load_script_structure(self, input_path: str) -> Dict[str, Any]:
    """
    Load a script structure from a JSON file.

    Args:
        input_path (str): Path to load the structure file from

    Returns:
        dict: Loaded script structure
    """
    input_path = Path(input_path)

    if not input_path.exists():
      raise FileNotFoundError(f"Script structure file not found: {input_path}")

    with open(input_path, 'r', encoding='utf-8') as f:
      script_structure = json.load(f)

    logger.info(f"Script structure loaded from {input_path}")
    return script_structure

  def _calculate_element_duration(self, element: Dict[str, Any],
                                  characters: Dict[str, Dict[str, Any]]) -> float:
    """
    Calculate the duration of a script element.

    Args:
        element (dict): Script element
        characters (dict): Character information

    Returns:
        float: Duration in seconds
    """
    if element['type'] == 'sound':
      # Get sound duration from description or use default
      duration = self.params['average_sound_duration']

      # Adjust based on modifiers
      if 'duration' in element:
        if element['duration'] == 'short':
          duration *= 0.5
        elif element['duration'] == 'long':
          duration *= 2.0
      return duration

    elif element['type'] == 'dialogue':
      # Calculate based on word count and speaking rate
      character = element['character']
      text = element['text']
      word_count = len(text.split())

      # Get character's speaking rate or use default
      words_per_minute = self.params['words_per_minute']

      if character in characters:
        char_profile = characters[character].get('voice_profile', {})

        # Adjust speaking rate based on character's speed
        if 'speed' in char_profile:
          if char_profile['speed'] == 'fast':
            words_per_minute *= 1.2
          elif char_profile['speed'] == 'slow':
            words_per_minute *= 0.85

      # Calculate duration in seconds
      duration = (word_count / words_per_minute) * 60

      # Apply emotion-based adjustments
      if 'emotion' in element:
        emotion = element['emotion'].lower()
        if emotion in ['excited', 'angry', 'furious', 'agitated']:
          duration *= 0.9  # Faster when excited or angry
        elif emotion in ['sad', 'solemn', 'grieving', 'melancholy']:
          duration *= 1.15  # Slower when sad
        elif emotion in ['thoughtful', 'considering', 'pondering']:
          duration *= 1.1  # Slightly slower with more pauses

      # Add extra time for internal thoughts
      if element.get('is_internal', False):
        duration *= 1.1  # Internal thoughts typically have more deliberate pacing

      return duration

  def _process_special_treatments(self, script_structure: Dict[str, Any]) -> None:
    """
    Process special treatments and add timing information.

    Args:
        script_structure (dict): Complete script structure
    """
    timeline = script_structure['timeline']
    treatments = script_structure.get('special_treatments', [])

    if not treatments:
      return

    for treatment in treatments:
      # Skip if not sound-related
      if treatment.get('type') != 'sound_treatment':
        continue

      # Find relevant scenes or entire script for the treatment
      if 'category' in treatment:
        category = treatment['category']

        # Create a mapping of all elements in each scene that match this category
        matched_elements = []

        for scene in timeline:
          for element in scene['elements']:
            if element['type'] == 'sound' and 'category' in element and element['category'] == category:
              matched_elements.append({
                'element': element,
                'scene': scene
              })

        # If we found matching elements, add timing info to the treatment
        if matched_elements:
          # Calculate starting and ending times
          start_time = min(item['element']['start_time'] for item in matched_elements)
          end_time = max(item['element']['start_time'] + item['element']['duration']
                         for item in matched_elements)

          treatment['start_time'] = start_time
          treatment['end_time'] = end_time
          treatment['duration'] = end_time - start_time
          treatment['affected_elements'] = [item['element'] for item in matched_elements]

      # Check if this treatment is narrative-linked
      if treatment.get('narrative_linked', False):
        # For narrative-linked treatments (like "tension increases"),
        # map to the full timeline
        treatment['start_time'] = 0
        treatment['end_time'] = script_structure['estimated_duration']
        treatment['duration'] = script_structure['estimated_duration']