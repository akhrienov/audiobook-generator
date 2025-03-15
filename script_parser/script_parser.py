#!/usr/bin/env python3
"""
Main Script Parser implementation for the Automated Audio Drama Generator.

This module acts as the coordinator for all the script parsing components,
bringing them together to parse a complete script.
"""

import os
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional

from .markdown_parser import MarkdownParser
from .character_extractor import CharacterExtractor
from .sound_cue_extractor import SoundCueExtractor
from .script_structure_builder import ScriptStructureBuilder

# Setup logging
logger = logging.getLogger(__name__)

class ScriptParser:
  """Main script parser coordinator."""

  def __init__(self, config=None):
    """
    Initialize the script parser.

    Args:
        config (dict, optional): Configuration options
    """
    self.config = config or {}

    # Initialize component parsers
    self.markdown_parser = MarkdownParser(config)
    self.character_extractor = CharacterExtractor(config)
    self.sound_extractor = SoundCueExtractor(config)
    self.structure_builder = ScriptStructureBuilder(config)

  def parse_script(self, script_path: str) -> Dict[str, Any]:
    """
    Parse a markdown script file into a structured format.

    Args:
        script_path (str): Path to the markdown script file

    Returns:
        dict: Structured script data with sections for metadata, characters, scenes, and production notes
    """
    script_path = Path(script_path)
    if not script_path.exists():
      raise FileNotFoundError(f"Script file not found: {script_path}")

    logger.info(f"Parsing script: {script_path}")

    # Read the script file
    with open(script_path, 'r', encoding='utf-8') as f:
      script_content = f.read()

    # Extract and process the various components of the script
    try:
      # Parse metadata from the script
      metadata = self._extract_metadata(script_content)
      logger.info(f"Extracted metadata for: {metadata.get('title', 'Untitled')}")

      # Extract character information
      characters = self.character_extractor.extract_characters(script_content)
      logger.info(f"Extracted {len(characters)} characters")

      # Extract scenes
      scenes = self._extract_scenes(script_content)
      logger.info(f"Extracted {len(scenes)} scenes")

      # Extract sound cues
      sound_cues = self.sound_extractor.extract_sound_cues(script_content)
      logger.info(f"Extracted {len(sound_cues)} sound cues")

      # Extract special sound treatments
      special_treatments = self.sound_extractor.extract_special_sound_treatments(script_content)
      logger.info(f"Extracted {len(special_treatments)} special sound treatments")

      # Extract production notes
      production_notes = self._extract_production_notes(script_content)

      # Build the unified script structure
      script_structure = self.structure_builder.build_script_structure(
        metadata, characters, scenes, sound_cues, special_treatments
      )

      # Add production notes to the structure
      script_structure['production_notes'] = production_notes

      # For backwards compatibility with tests, add the scenes directly
      script_structure['scenes'] = scenes

      return script_structure

    except Exception as e:
      logger.error(f"Error parsing script: {e}")
      raise

  def _extract_metadata(self, script_content: str) -> Dict[str, str]:
    """
    Extract metadata from script content (title, premise).

    Args:
        script_content (str): Raw script content

    Returns:
        dict: Script metadata
    """
    metadata = {}

    # Extract sections using the markdown parser
    sections = self.markdown_parser.extract_sections(script_content)

    # Get title
    if 'TITLE' in sections:
      metadata['title'] = sections['TITLE']

    # Get premise
    if 'PREMISE' in sections:
      metadata['premise'] = sections['PREMISE']

    return metadata

  def _extract_scenes(self, script_content: str) -> List[Dict[str, Any]]:
    """
    Extract scenes with dialogue and sound elements.

    Args:
        script_content (str): Raw script content

    Returns:
            list: Scenes with dialogue and sound elements
    """
    scenes = []

    # Extract sections using the markdown parser
    sections = self.markdown_parser.extract_sections(script_content)

    # Process each section that isn't a special section
    special_sections = ['TITLE', 'PREMISE', 'SPEAKER NOTES', 'PRODUCTION NOTES']

    for name, content in sections.items():
      if name in special_sections:
        continue

      # Parse the scene content
      elements = self.markdown_parser.parse_scene(content)

      # Additional debug logging
      logger.debug(f"Scene {name} has {len(elements)} elements")
      sound_count = sum(1 for e in elements if e['type'] == 'sound')
      dialogue_count = sum(1 for e in elements if e['type'] == 'dialogue')
      logger.debug(f"  Sound elements: {sound_count}")
      logger.debug(f"  Dialogue elements: {dialogue_count}")

      scenes.append({
        'name': name,
        'elements': elements
      })

    return scenes

  def _extract_production_notes(self, script_content: str) -> Dict[str, Any]:
    """
    Extract production notes from script content.

    Args:
        script_content (str): Raw script content

    Returns:
        dict: Production notes and special instructions
    """
    production_notes = {}

    # Extract sections using the markdown parser
    sections = self.markdown_parser.extract_sections(script_content)

    # Get production notes if present
    if 'PRODUCTION NOTES' in sections:
      notes_content = sections['PRODUCTION NOTES']

      # Extract estimated runtime
      import re
      runtime_match = re.search(r'\*\*Estimated Runtime:\*\*\s*(.+?)$', notes_content, re.MULTILINE)
      if runtime_match:
        production_notes['estimated_runtime'] = runtime_match.group(1).strip()

      # Extract emotional moments
      emotional_moments = re.search(r'\*\*Key Emotional Moments:\*\*\s*\n(.*?)(?=\*\*|\Z)',
                                    notes_content, re.DOTALL)
      if emotional_moments:
        moments = re.findall(r'\d+\.\s*(.+?)$', emotional_moments.group(1), re.MULTILINE)
        production_notes['emotional_moments'] = moments

      # Extract any other production notes sections
      other_sections = re.finditer(r'\*\*(.+?):\*\*\s*\n(.*?)(?=\*\*|\Z)',
                                   notes_content, re.DOTALL)

      for match in other_sections:
        section_name = match.group(1).strip()
        section_content = match.group(2).strip()

        # Skip already processed sections
        if section_name in ['Estimated Runtime', 'Key Emotional Moments']:
          continue

        # Check if it's a numbered list
        if re.search(r'^\d+\.', section_content, re.MULTILINE):
          items = re.findall(r'\d+\.\s*(.+?)$', section_content, re.MULTILINE)
          production_notes[section_name.lower().replace(' ', '_')] = items
        else:
          production_notes[section_name.lower().replace(' ', '_')] = section_content

    return production_notes