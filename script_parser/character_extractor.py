#!/usr/bin/env python3
"""
Character Extractor for the Automated Audio Drama Generator.

This module extracts character information from scripts and builds
voice profiles for each character based on their descriptions.
"""

import re
import logging
from typing import Dict, List, Any, Optional

# Setup logging
logger = logging.getLogger(__name__)

class CharacterExtractor:
  """Extracts character information and builds voice profiles."""

  def __init__(self, config=None):
    """
    Initialize the character extractor.

    Args:
        config (dict, optional): Configuration options
    """
    self.config = config or {}
    self.default_voice_traits = {
      'pitch': 'medium',
      'speed': 'normal',
      'accent': 'neutral',
      'age': 'adult',
      'gender': 'neutral',
      'qualities': []
    }

    # Load configuration for character extraction
    if config and 'script_parser' in config and 'character' in config['script_parser']:
      char_config = config['script_parser']['character']
      if 'default_voice_traits' in char_config:
        self.default_voice_traits.update(char_config['default_voice_traits'])

  def extract_characters(self, script_content: str) -> Dict[str, Dict[str, Any]]:
    """
    Extract character information from script content.

    Args:
        script_content (str): Raw script content

    Returns:
        dict: Characters with their descriptions and voice profiles
    """
    characters = {}

    # Find the SPEAKER NOTES section using more flexible regex
    speaker_notes_match = re.search(
      r'## SPEAKER NOTES\s*\n(.*?)(?=^##|\Z)',
      script_content, re.MULTILINE | re.DOTALL
    )

    if not speaker_notes_match:
      logger.warning("No SPEAKER NOTES section found in script")
      return characters

    speaker_notes = speaker_notes_match.group(1)

    # Print debug info to see what we're working with
    logger.debug(f"Speaker notes content: {speaker_notes[:200]}...")

    # Find the CHARACTERS subsection - try different patterns
    characters_section = ""
    patterns = [
      r'\*\*CHARACTERS:\*\*\s*\n(.*?)(?=\*\*Special Audio Considerations|\Z)',
      r'\*\*CHARACTERS:\*\*\s*\n(.*?)(?=\*\*|\Z)',
      r'CHARACTERS:(.*?)(?=\*\*|\Z)'
    ]

    for pattern in patterns:
      match = re.search(pattern, speaker_notes, re.DOTALL)
      if match:
        characters_section = match.group(1).strip()
        break

    if not characters_section:
      logger.warning("No CHARACTERS subsection found in SPEAKER NOTES")
      return characters

    logger.debug(f"Characters section content: {characters_section[:200]}...")

    # Process each character entry directly with simple line-by-line approach
    lines = characters_section.split('\n')
    for line in lines:
      line = line.strip()
      if not line:
        continue

      # Look for patterns like "**John** - Description"
      char_match = re.match(r'\*\*([^*]+)\*\*\s*-\s*(.+)', line)
      if char_match:
        character_name = char_match.group(1).strip()
        description = char_match.group(2).strip()

        logger.debug(f"Found character: {character_name} with desc: {description[:50]}...")

        # Build voice profile
        voice_profile = self.build_voice_profile(description)

        # Add voice_attributes for backward compatibility with tests
        voice_attributes = {
          'pitch': voice_profile['pitch'],
          'speed': voice_profile['speed'],
          'accent': voice_profile['accent'],
        }
        if 'qualities' in voice_profile:
            voice_attributes['qualities'] = voice_profile['qualities']
        if 'effects' in voice_profile:
          voice_attributes['effects'] = voice_profile['effects']

        characters[character_name] = {
          'name': character_name,
          'description': description,
          'voice_profile': voice_profile,
          'voice_attributes': voice_attributes
        }

    # Extract special audio information
    special_audio = self.extract_special_audio_notes(speaker_notes)

    if special_audio:
      # Add special audio notes to relevant characters
      for character_name in characters:
        for note in special_audio:
          if character_name in note:
            if 'special_audio' not in characters[character_name]:
              characters[character_name]['special_audio'] = []
            characters[character_name]['special_audio'].append(note)

    logger.info(f"Extracted {len(characters)} characters")
    return characters

  def build_voice_profile(self, description: str) -> Dict[str, Any]:
    """
    Build a voice profile based on character description.

    Args:
        description (str): Character description text

    Returns:
        dict: Voice profile with parameters for voice generation
    """
    # Start with default voice traits
    profile = self.default_voice_traits.copy()

    # Extract gender information
    if re.search(r'\b(he|him|his|male|man)\b', description, re.IGNORECASE):
      profile['gender'] = 'male'
    elif re.search(r'\b(she|her|hers|female|woman)\b', description, re.IGNORECASE):
      profile['gender'] = 'female'

    # Extract age information
    if re.search(r'\b(child|young|kid|youth|teenage|teenager)\b', description, re.IGNORECASE):
      profile['age'] = 'young'
    elif re.search(r'\b(elder|elderly|old|senior|ancient)\b', description, re.IGNORECASE):
      profile['age'] = 'old'

    # Extract pitch information
    if re.search(r'\b(high|higher|falsetto|soprano)\b', description, re.IGNORECASE):
      profile['pitch'] = 'high'
    elif re.search(r'\b(low|lower|deep|bass|baritone)\b', description, re.IGNORECASE):
      profile['pitch'] = 'low'
    elif re.search(r'\bmid-range\b|\bmidrange\b|\bmedium\b', description, re.IGNORECASE):
      profile['pitch'] = 'medium'

    # Extract speech rate
    if re.search(r'\b(fast|quick|rapid|swift)\b', description, re.IGNORECASE):
      profile['speed'] = 'fast'
    elif re.search(r'\b(slow|deliberate|measured|calm|relaxed)\b', description, re.IGNORECASE):
      profile['speed'] = 'slow'

    # Extract voice qualities
    qualities = []
    quality_terms = [
      'raspy', 'gruff', 'rough', 'smooth', 'soft', 'harsh', 'breathy',
      'nasal', 'melodic', 'monotone', 'robotic', 'warm', 'cold', 'shaky',
      'confident', 'authoritative', 'gentle', 'powerful', 'weak', 'timid',
      'crisp', 'official', 'commanding', 'grumbly', 'squeaky'
    ]

    for quality in quality_terms:
      if re.search(r'\b' + quality + r'\b', description, re.IGNORECASE):
        qualities.append(quality)

    if qualities:
      profile['qualities'] = qualities

    # Extract accent information
    accent_match = re.search(r'\b(accent|dialect)\b.*\b([a-z]+)\b', description, re.IGNORECASE)
    if accent_match:
      profile['accent'] = accent_match.group(2).lower()
    else:
      # Check for common accents/dialects
      accents = [
        'british', 'american', 'australian', 'scottish', 'irish', 'french',
        'german', 'russian', 'spanish', 'italian', 'japanese', 'chinese',
        'indian', 'southern', 'midwestern', 'new york', 'boston', 'texan',
        'coastal'
      ]

      for accent in accents:
        if re.search(r'\b' + accent + r'\b', description, re.IGNORECASE):
          profile['accent'] = accent.lower()
          break

    # Extract special effects
    effects = []
    effect_terms = ['echo', 'reverb', 'distortion', 'whisper', 'modulated']

    for effect in effect_terms:
      if re.search(r'\b' + effect + r'\b', description, re.IGNORECASE):
        effects.append(effect)

    if effects:
      profile['effects'] = effects

    # Calculate numerical parameters for voice generation
    profile['numerical_params'] = self.calculate_numerical_parameters(profile)

    return profile

  def calculate_numerical_parameters(self, profile: Dict[str, Any]) -> Dict[str, float]:
    """
    Calculate numerical parameters for voice generation based on profile.

    Args:
        profile (dict): Voice profile with qualitative parameters

    Returns:
        dict: Numerical parameters for voice generation
    """
    params = {
      'pitch_shift': 0.0,  # Semitones, 0 = no shift
      'speed_factor': 1.0,  # 1.0 = normal speed
      'formant_shift': 0.0,  # Formant shift for accent/gender
      'breathiness': 0.0,  # 0.0 to 1.0
      'roughness': 0.0,  # 0.0 to 1.0
      'vocal_tract_length': 1.0,  # 1.0 = normal
    }

    # Adjust pitch based on profile
    if profile['pitch'] == 'high':
      params['pitch_shift'] = 3.0  # Shift up by 3 semitones
    elif profile['pitch'] == 'low':
      params['pitch_shift'] = -3.0  # Shift down by 3 semitones

    # Adjust speed based on profile
    if profile['speed'] == 'fast':
      params['speed_factor'] = 1.2  # 20% faster
    elif profile['speed'] == 'slow':
      params['speed_factor'] = 0.85  # 15% slower

    # Adjust formants based on age and gender
    if profile['gender'] == 'female':
      params['formant_shift'] = 0.3
      params['vocal_tract_length'] = 0.85
    elif profile['gender'] == 'male':
      params['formant_shift'] = -0.2
      params['vocal_tract_length'] = 1.15

    if profile['age'] == 'young':
      params['formant_shift'] += 0.2
      params['vocal_tract_length'] *= 0.9
    elif profile['age'] == 'old':
      params['formant_shift'] -= 0.2
      params['vocal_tract_length'] *= 1.05

    # Adjust for voice qualities
    if 'qualities' in profile:
      qualities = profile['qualities']

      if 'raspy' in qualities or 'rough' in qualities or 'gruff' in qualities:
        params['roughness'] = 0.4

      if 'soft' in qualities or 'gentle' in qualities:
        params['roughness'] -= 0.2
        params['breathiness'] = 0.3

      if 'breathy' in qualities:
        params['breathiness'] = 0.5

      if 'nasal' in qualities:
        params['formant_shift'] += 0.15

      if 'powerful' in qualities or 'commanding' in qualities:
        params['roughness'] += 0.1
        params['breathiness'] -= 0.1

      if 'timid' in qualities or 'weak' in qualities:
        params['breathiness'] += 0.2

    # Ensure all parameters are within valid ranges
    params['breathiness'] = max(0.0, min(1.0, params['breathiness']))
    params['roughness'] = max(0.0, min(1.0, params['roughness']))

    return params

  def extract_special_audio_notes(self, speaker_notes: str) -> List[str]:
    """
    Extract special audio considerations from speaker notes.

    Args:
        speaker_notes (str): Speaker notes text

    Returns:
        list: Special audio considerations
    """
    considerations = []

    # Find the Special Audio Considerations subsection
    special_audio_match = re.search(
      r'\*\*Special Audio Considerations:\*\*\s*\n(.*?)(?=\*\*|\Z)',
      speaker_notes, re.DOTALL
    )

    if special_audio_match:
      special_audio_text = special_audio_match.group(1)

      # Extract bullet points
      bullet_points = re.findall(r'- (.+?)$', special_audio_text, re.MULTILINE)
      considerations = [point.strip() for point in bullet_points]

    return considerations

  def get_narrator_voice_profile(self, characters: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """
    Get or create a narrator voice profile.

    Args:
        characters (dict): Character dictionary

    Returns:
        dict: Narrator voice profile
    """
    # Check if "Narrator" is already defined in characters
    if "Narrator" in characters:
      return characters["Narrator"]["voice_profile"]

    # Create a default narrator voice profile
    narrator_profile = {
      'gender': 'neutral',
      'age': 'adult',
      'pitch': 'medium',
      'speed': 'normal',
      'accent': 'neutral',
      'qualities': ['clear', 'engaging'],
      'numerical_params': {
        'pitch_shift': 0.0,
        'speed_factor': 1.0,
        'formant_shift': 0.0,
        'breathiness': 0.1,
        'roughness': 0.0,
        'vocal_tract_length': 1.0
      }
    }

    return narrator_profile