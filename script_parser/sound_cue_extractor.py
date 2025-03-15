#!/usr/bin/env python3
"""
Sound Cue Extractor for the Automated Audio Drama Generator.

This module extracts sound effect cues from scripts and categorizes them
for use by the sound manager.
"""

import re
import logging
from typing import Dict, List, Any, Optional, Tuple

# Setup logging
logger = logging.getLogger(__name__)

class SoundCueExtractor:
  """Extracts and categorizes sound cues from scripts."""

  def __init__(self, config=None):
    """
    Initialize the sound cue extractor.

    Args:
        config (dict, optional): Configuration options
    """
    self.config = config or {}

    # Default regex pattern for sound cues
    self.sound_cue_pattern = r'\[sound:\s*(.+?)\]'

    # Sound categories and their related keywords
    self.sound_categories = {
      'ambient': [
        'ambient', 'background', 'atmosphere', 'room tone', 'environment',
        'wind', 'rain', 'forest', 'city', 'crowd', 'traffic', 'restaurant',
        'birds', 'ocean', 'waves', 'fire', 'crackling'
      ],
      'transition': [
        'transition', 'flashback', 'dream', 'memory', 'time passing',
        'fade', 'whoosh', 'swoosh', 'scene change'
      ],
      'impact': [
        'crash', 'bang', 'explosion', 'slam', 'thud', 'hit', 'punch',
        'collision', 'breaking', 'smash', 'shatter', 'impact'
      ],
      'object': [
        'door', 'window', 'car', 'engine', 'machine', 'phone', 'clock',
        'glass', 'paper', 'fabric', 'footsteps', 'knock', 'bell', 'alarm'
      ],
      'weather': [
        'rain', 'thunder', 'lightning', 'wind', 'storm', 'blizzard',
        'snow', 'hail', 'hurricane', 'tornado'
      ],
      'animal': [
        'dog', 'cat', 'bird', 'wolf', 'howl', 'roar', 'chirp', 'growl',
        'bark', 'meow', 'neigh', 'animal'
      ],
      'electronic': [
        'beep', 'static', 'computer', 'radio', 'television', 'phone',
        'alarm', 'electronic', 'digital', 'interference'
      ],
      'human': [
        'whisper', 'cough', 'laugh', 'cry', 'scream', 'sigh', 'gasp',
        'breath', 'heartbeat', 'footsteps', 'clap', 'snap', 'whistle'
      ],
      'musical': [
        'music', 'melody', 'theme', 'song', 'tune', 'jingle', 'chord',
        'piano', 'guitar', 'drum', 'orchestra', 'band', 'instrument'
      ]
    }

    # Override with config if provided
    if config and 'script_parser' in config and 'sound' in config['script_parser']:
      sound_config = config['script_parser']['sound']
      if 'cue_pattern' in sound_config:
        self.sound_cue_pattern = sound_config['cue_pattern']
      if 'categories' in sound_config:
        self.sound_categories.update(sound_config['categories'])

  def extract_sound_cues(self, script_content: str) -> List[Dict[str, Any]]:
    """
    Extract sound cues from script content.

    Args:
        script_content (str): Raw script content

    Returns:
        list: Sound cues with type, description, category, and scene info
    """
    sound_cues = []

    # Find all sound cues in the script
    cue_matches = re.finditer(self.sound_cue_pattern, script_content, re.MULTILINE)

    for match in cue_matches:
      description = match.group(1).strip()

      # Get position information to determine scene context
      position = match.start()
      scene_info = self._find_scene_for_position(script_content, position)

      # Categorize the sound cue
      category = self._categorize_sound_cue(description)

      # Parse any intensity or duration modifiers
      modifiers = self._parse_modifiers(description)

      sound_cue = {
        'type': 'sound',
        'description': description,
        'category': category,
        'scene': scene_info['name'] if scene_info else None,
        'position': position
      }

      # Add any modifiers if found
      if modifiers:
        sound_cue.update(modifiers)

      sound_cues.append(sound_cue)

    logger.info(f"Extracted {len(sound_cues)} sound cues")
    return sound_cues

  def _find_scene_for_position(self, script_content: str, position: int) -> Optional[Dict[str, Any]]:
    """
    Find the scene that contains the given position.

    Args:
        script_content (str): Raw script content
        position (int): Character position in the script

    Returns:
        dict or None: Scene information or None if not found
    """
    # Find all scene headers
    scene_headers = re.finditer(r'^## (.+?)$', script_content, re.MULTILINE)

    current_scene = None
    current_position = 0

    for match in scene_headers:
      scene_position = match.start()
      scene_name = match.group(1).strip()

      # Skip non-scene sections
      if scene_name in ['PREMISE', 'SPEAKER NOTES', 'PRODUCTION NOTES']:
        continue

      if scene_position <= position:
        current_scene = {
          'name': scene_name,
          'position': scene_position
        }
        current_position = scene_position
      else:
        # We've gone past the position, so return the last scene
        break

    return current_scene

  def _categorize_sound_cue(self, description: str) -> str:
    """
    Categorize a sound cue based on its description.

    Args:
        description (str): Sound cue description

    Returns:
        str: Sound category
    """
    description_lower = description.lower()

    # First handle special cases that need prioritized handling

    # Weather-related sounds
    weather_keywords = ['rain', 'thunder', 'lightning', 'storm', 'wind', 'snow', 'hail', 'blizzard']
    for keyword in weather_keywords:
      if keyword in description_lower:
        return 'weather'

    # Electronic device sounds - fix for "phone ringing"
    electronic_keywords = ['phone', 'beep', 'computer', 'electronic', 'digital', 'alarm', 'static']
    for keyword in electronic_keywords:
      if keyword in description_lower:
        return 'electronic'

    # Then check all other categories
    for category, keywords in self.sound_categories.items():
      for keyword in keywords:
        if keyword in description_lower:
          return category

    # Default category if no match is found
    return 'misc'

  def _parse_modifiers(self, description: str) -> Dict[str, Any]:
    """
    Parse modifiers from the sound cue description.

    Args:
        description (str): Sound cue description

    Returns:
        dict: Extracted modifiers (intensity, duration, etc.)
    """
    modifiers = {}

    # Check for intensity modifiers
    intensity_match = re.search(
      r'\b(increasing|decreasing|intensifying|fading|growing|building|diminishing)\b',
      description, re.IGNORECASE
    )

    if intensity_match:
      intensity_word = intensity_match.group(1).lower()

      if intensity_word in ['increasing', 'intensifying', 'growing', 'building']:
        modifiers['intensity_change'] = 'increasing'
      elif intensity_word in ['decreasing', 'fading', 'diminishing']:
        modifiers['intensity_change'] = 'decreasing'

    # Check for duration hints
    duration_match = re.search(
      r'\b(brief|short|long|extended|continuous|sustained|quick)\b',
      description, re.IGNORECASE
    )

    if duration_match:
      duration_word = duration_match.group(1).lower()

      if duration_word in ['brief', 'short', 'quick']:
        modifiers['duration'] = 'short'
      elif duration_word in ['long', 'extended', 'continuous', 'sustained']:
        modifiers['duration'] = 'long'

    # Check for volume modifiers
    volume_match = re.search(
      r'\b(loud|soft|quiet|gentle|strong|heavy|light|faint|distant)\b',
      description, re.IGNORECASE
    )

    if volume_match:
      volume_word = volume_match.group(1).lower()

      if volume_word in ['loud', 'strong', 'heavy']:
        modifiers['volume'] = 'loud'
      elif volume_word in ['soft', 'quiet', 'gentle', 'light', 'faint', 'distant']:
        modifiers['volume'] = 'soft'

    return modifiers

  def extract_special_sound_treatments(self, script_content: str) -> List[Dict[str, Any]]:
    """
    Extract special sound treatments from the script.

    Args:
        script_content (str): Raw script content

    Returns:
        list: Special sound treatments with rules and parameters
    """
    treatments = []

    # Find the SPEAKER NOTES section
    speaker_notes_match = re.search(
      r'^## SPEAKER NOTES\s*\n(.*?)(?=^##|\Z)',
      script_content, re.MULTILINE | re.DOTALL
    )

    if not speaker_notes_match:
      return treatments

    speaker_notes = speaker_notes_match.group(1)

    # Find the Special Audio Considerations subsection
    special_audio_match = re.search(
      r'\*\*Special Audio Considerations:\*\*\s*\n(.*?)(?=\*\*|\Z)',
      speaker_notes, re.DOTALL
    )

    if not special_audio_match:
      return treatments

    special_audio_text = special_audio_match.group(1)

    # Extract bullet points
    bullet_points = re.findall(r'- (.+?)$', special_audio_text, re.MULTILINE)

    for point in bullet_points:
      point = point.strip()

      # Process special sound treatments
      treatment = self._parse_special_treatment(point)
      if treatment:
        treatments.append(treatment)

    # Also check PRODUCTION NOTES section for treatments
    production_notes_match = re.search(
      r'^## PRODUCTION NOTES\s*\n(.*?)(?=^##|\Z)',
      script_content, re.MULTILINE | re.DOTALL
    )

    if production_notes_match:
      production_notes = production_notes_match.group(1)

      # Look for Special Audio Treatment subsection
      audio_treatment_match = re.search(
        r'\*\*Special Audio Treatment:\*\*\s*\n(.*?)(?=\*\*|\Z)',
        production_notes, re.DOTALL
      )

      if audio_treatment_match:
        audio_treatment_text = audio_treatment_match.group(1)

        # Extract numbered items
        treatment_items = re.findall(r'\d+\.\s*(.+?)$', audio_treatment_text, re.MULTILINE)

        for item in treatment_items:
          treatment = self._parse_special_treatment(item.strip())
          if treatment:
            treatments.append(treatment)

    logger.info(f"Extracted {len(treatments)} special sound treatments")
    return treatments

  def _parse_special_treatment(self, text: str) -> Optional[Dict[str, Any]]:
    """
    Parse a special sound treatment description.

    Args:
        text (str): Treatment description

    Returns:
        dict or None: Parsed treatment or None if not applicable
    """
    # Check if this is a sound-related treatment
    sound_types = [
      'sound', 'audio', 'effect', 'sfx', 'ambient', 'background',
      'storm', 'rain', 'wind', 'foghorn', 'music', 'thunder'
    ]

    is_sound_related = False
    for sound_type in sound_types:
      if sound_type in text.lower():
        is_sound_related = True
        break

    if not is_sound_related:
      return None

    # Extract key details
    treatment = {
      'description': text,
      'type': 'sound_treatment'
    }

    # Check for gradual change indicators
    if any(word in text.lower() for word in ['gradual', 'gradually', 'increase', 'intensify', 'build']):
      treatment['change_type'] = 'gradual'

      # Determine direction of change
      if any(word in text.lower() for word in ['increase', 'intensify', 'louder', 'stronger']):
        treatment['direction'] = 'increasing'
      elif any(word in text.lower() for word in ['decrease', 'fade', 'softer', 'quieter']):
        treatment['direction'] = 'decreasing'

    # Check for sound categories
    for category, keywords in self.sound_categories.items():
      for keyword in keywords:
        if keyword in text.lower():
          treatment['category'] = category
          break
      if 'category' in treatment:
        break

    # Check for relationship to narrative elements
    if any(word in text.lower() for word in ['narrative', 'tension', 'mood', 'emotional']):
      treatment['narrative_linked'] = True

    return treatment

  def extract_ambient_sounds(self, sound_cues: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Extract ambient sounds by scene from sound cues.

    Args:
        sound_cues (list): Sound cues

    Returns:
        dict: Ambient sounds organized by scene
    """
    ambient_by_scene = {}

    for cue in sound_cues:
      # Only process ambient sound cues
      if cue['category'] != 'ambient':
        continue

      scene = cue['scene']
      if not scene:
        continue

      if scene not in ambient_by_scene:
        ambient_by_scene[scene] = []

      ambient_by_scene[scene].append(cue)

    return ambient_by_scene