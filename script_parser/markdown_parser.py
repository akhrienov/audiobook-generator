#!/usr/bin/env python3
"""
Markdown Parser for the Automated Audio Drama Generator.

This module converts markdown-formatted scripts into HTML and provides
helper functions for extracting structured content.
"""

import re
import logging
import markdown
from bs4 import BeautifulSoup
from typing import Dict, List, Any, Optional, Tuple

# Setup logging
logger = logging.getLogger(__name__)

class MarkdownParser:
  """Parser for converting markdown to structured content."""

  def __init__(self, config=None):
    """
    Initialize the markdown parser.

    Args:
        config (dict, optional): Configuration options
    """
    self.config = config or {}
    # Configure markdown extensions
    self.md_extensions = ['extra', 'nl2br', 'sane_lists']

    if config and 'script_parser' in config and 'markdown_extensions' in config['script_parser']:
      self.md_extensions = config['script_parser']['markdown_extensions']

  def md_to_html(self, markdown_text: str) -> str:
    """
    Convert markdown text to HTML.

    Args:
        markdown_text (str): Markdown-formatted text

    Returns:
        str: HTML-formatted text
    """
    return markdown.markdown(markdown_text, extensions=self.md_extensions)

  def md_to_soup(self, markdown_text: str) -> BeautifulSoup:
    """
    Convert markdown text to BeautifulSoup object.

    Args:
        markdown_text (str): Markdown-formatted text

    Returns:
        BeautifulSoup: BeautifulSoup object for HTML parsing
    """
    html = self.md_to_html(markdown_text)
    return BeautifulSoup(html, 'html.parser')

  def extract_sections(self, markdown_text: str) -> Dict[str, str]:
    """
    Extract main sections from the markdown script.

    Args:
        markdown_text (str): Markdown-formatted script

    Returns:
        dict: Sections keyed by their heading
    """
    sections = {}

    # Extract the title (# Title), allowing for indentation
    title_match = re.search(r'^\s*#\s+(.+?)\s*$', markdown_text, re.MULTILINE)
    if title_match:
      sections['TITLE'] = title_match.group(1).strip()

    # Extract all level 2 headers with a more flexible pattern that handles indentation
    section_pattern = r'^\s*##\s+(.+?)\s*$\n([\s\S]*?)(?=^\s*##\s+|\s*$)'
    matches = re.finditer(section_pattern, markdown_text, re.MULTILINE)

    for match in matches:
      heading = match.group(1).strip()
      content = match.group(2).strip()
      sections[heading] = content

    return sections

  def parse_character_section(self, character_section: str) -> Dict[str, Dict[str, Any]]:
    """
    Parse the character section into structured character data.

    Args:
        character_section (str): Character section text

    Returns:
        dict: Character information keyed by character name
    """
    characters = {}

    # Print debug info
    logger.debug(f"Character section content: {character_section[:200]}...")

    # Try different patterns to find the CHARACTERS subsection
    character_block = ""
    patterns = [
      r'\*\*CHARACTERS:\*\*\s*\n(.*?)(?=\*\*Special Audio Considerations|\Z)',
      r'\*\*CHARACTERS:\*\*\s*\n(.*?)(?=\*\*|\Z)',
      r'CHARACTERS:(.*?)(?=\*\*|\Z)'
    ]

    for pattern in patterns:
      match = re.search(pattern, character_section, re.DOTALL)
      if match:
        character_block = match.group(1).strip()
        break

    if not character_block:
      logger.warning("Could not find CHARACTERS subsection")
      return characters

    # Process line by line for more reliability
    lines = character_block.split('\n')
    for line in lines:
      line = line.strip()
      if not line:
        continue

      # Look for patterns like "**John** - Description"
      char_match = re.match(r'\*\*([^*]+)\*\*\s*-\s*(.+)', line)
      if char_match:
        name = char_match.group(1).strip()
        description = char_match.group(2).strip()

        logger.debug(f"Found character: {name} with desc: {description[:50]}...")

        characters[name] = {
          'description': description,
          'voice_attributes': self._extract_voice_attributes(description)
        }

    logger.info(f"Parsed {len(characters)} characters")
    return characters

  def _extract_voice_attributes(self, description: str) -> Dict[str, Any]:
    """
    Extract voice attributes from a character description.

    Args:
        description (str): Character description text

    Returns:
        dict: Voice attributes
    """
    attributes = {
      'gender': self._detect_gender(description),
      'age': self._detect_age(description),
      'qualities': self._detect_qualities(description),
      'pitch': self._detect_pitch(description),
      'speed': self._detect_speed(description),
      'accent': self._detect_accent(description),
    }

    return attributes

  def _detect_gender(self, description: str) -> str:
    """
    Detect gender from description.

    Args:
        description (str): Character description

    Returns:
        str: Detected gender or 'neutral'
    """
    if re.search(r'\b(he|him|his|male|man)\b', description, re.IGNORECASE):
      return 'male'
    elif re.search(r'\b(she|her|hers|female|woman)\b', description, re.IGNORECASE):
      return 'female'
    else:
      return 'neutral'

  def _detect_age(self, description: str) -> str:
    """
    Detect age category from description.

    Args:
        description (str): Character description

    Returns:
        str: Age category
    """
    if re.search(r'\b(child|young|kid|youth|teenage|teenager)\b', description, re.IGNORECASE):
      return 'young'
    elif re.search(r'\b(elder|elderly|old|senior|ancient)\b', description, re.IGNORECASE):
      return 'old'
    else:
      return 'adult'

  def _detect_qualities(self, description: str) -> List[str]:
    """
    Detect voice qualities from description.

    Args:
        description (str): Character description

    Returns:
        list: Detected voice qualities
    """
    qualities = []
    quality_terms = [
      'raspy', 'gruff', 'rough', 'smooth', 'soft', 'harsh', 'breathy',
      'nasal', 'melodic', 'monotone', 'robotic', 'warm', 'cold', 'shaky',
      'confident', 'authoritative', 'gentle', 'powerful', 'weak', 'timid'
    ]

    for quality in quality_terms:
      if re.search(r'\b' + quality + r'\b', description, re.IGNORECASE):
        qualities.append(quality)

    return qualities

  def _detect_pitch(self, description: str) -> str:
    """
    Detect pitch from description.

    Args:
        description (str): Character description

    Returns:
        str: Pitch category
    """
    if re.search(r'\b(high|higher|falsetto|soprano)\b', description, re.IGNORECASE):
      return 'high'
    elif re.search(r'\b(low|lower|deep|bass|baritone)\b', description, re.IGNORECASE):
      return 'low'
    else:
      return 'medium'

  def _detect_speed(self, description: str) -> str:
    """
    Detect speaking speed from description.

    Args:
        description (str): Character description

    Returns:
        str: Speed category
    """
    if re.search(r'\b(fast|quick|rapid|swift)\b', description, re.IGNORECASE):
      return 'fast'
    elif re.search(r'\b(slow|deliberate|measured|calm|relaxed)\b', description, re.IGNORECASE):
      return 'slow'
    else:
      return 'normal'

  def _detect_accent(self, description: str) -> str:
    """
    Detect accent from description.

    Args:
        description (str): Character description

    Returns:
        str: Detected accent or 'neutral'
    """
    accent_match = re.search(r'\b(accent|dialect)\b.*\b([a-z]+)\b', description, re.IGNORECASE)
    if accent_match:
      return accent_match.group(2).lower()

    # Check for common accents/dialects
    accents = [
      'british', 'american', 'australian', 'scottish', 'irish', 'french',
      'german', 'russian', 'spanish', 'italian', 'japanese', 'chinese',
      'indian', 'southern', 'midwestern', 'new york', 'boston', 'texan'
    ]

    for accent in accents:
      if re.search(r'\b' + accent + r'\b', description, re.IGNORECASE):
        return accent.lower()

    return 'neutral'

  def parse_scene(self, scene_content: str) -> List[Dict[str, Any]]:
    """
    Parse a scene into a sequence of elements (dialogue and sound cues).

    Args:
        scene_content (str): Scene content text

    Returns:
        list: Ordered list of scene elements
    """
    elements = []

    # Process the scene line by line
    lines = scene_content.split('\n')

    for line in lines:
      line = line.strip()
      if not line:
        continue

      # Check for sound cue
      sound_match = re.search(r'\[sound:\s*(.+?)\]', line)
      if sound_match:
        elements.append({
          'type': 'sound',
          'description': sound_match.group(1).strip()
        })
        continue

      # Check for character dialogue - improved pattern
      dialogue_patterns = [
        r'\*\*(.+?)\*\*:\s*(.+)$',  # Standard: **Character:** Text
        r'\*\*(.+?)\*\*\s*\((.+?)\):\s*(.+)$',  # With emotion: **Character** (emotion): Text
      ]

      for pattern in dialogue_patterns:
        dialogue_match = re.search(pattern, line)
        if dialogue_match:
          # Check which pattern matched
          if len(dialogue_match.groups()) == 2:
            # Standard pattern
            character = dialogue_match.group(1).strip()
            text = dialogue_match.group(2).strip()

            dialogue_element = {
              'type': 'dialogue',
              'character': character,
              'text': text
            }

            # Check for emotion in parentheses at start of text
            emotion_match = re.match(r'\((.+?)\)\s*(.+)', text)
            if emotion_match:
              dialogue_element['emotion'] = emotion_match.group(1).strip()
              dialogue_element['text'] = emotion_match.group(2).strip()

          else:
            # Pattern with inline emotion
            character = dialogue_match.group(1).strip()
            emotion = dialogue_match.group(2).strip()
            text = dialogue_match.group(3).strip()

            dialogue_element = {
              'type': 'dialogue',
              'character': character,
              'emotion': emotion,
              'text': text
            }

          # Check for internal thoughts (text in asterisks)
          thought_match = re.search(r'\*(.+?)\*', dialogue_element['text'])
          if thought_match:
            # If the entire text is in asterisks, mark as internal
            if thought_match.group(0) == dialogue_element['text']:
              dialogue_element['is_internal'] = True
              dialogue_element['text'] = thought_match.group(1).strip()
            # Otherwise, mark that there's an internal thought within the text
            else:
              dialogue_element['has_internal'] = True

          elements.append(dialogue_element)
          break  # Break the pattern loop if we found a match

      # If line wasn't processed as sound or dialogue and contains "Narrator:"
      if "Narrator:" in line and not any(e in elements for e in [{'type': 'sound'}, {'type': 'dialogue'}]):
        narrator_match = re.search(r'Narrator:\s*(.+)', line)
        if narrator_match:
          elements.append({
            'type': 'dialogue',
            'character': 'Narrator',
            'text': narrator_match.group(1).strip()
          })

    logger.debug(f"Parsed {len(elements)} elements from scene")

    # Log types of elements
    element_types = [e['type'] for e in elements]
    logger.debug(f"Element types: {element_types}")

    return elements

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
      r'\*\*Special Audio Considerations:\*\*\s*\n(.*?)(?=^##|\Z)',
      speaker_notes, re.MULTILINE | re.DOTALL
    )

    if special_audio_match:
      special_audio_text = special_audio_match.group(1)

      # Extract bullet points
      bullet_points = re.findall(r'- (.+?)$', special_audio_text, re.MULTILINE)
      considerations = [point.strip() for point in bullet_points]

    return considerations