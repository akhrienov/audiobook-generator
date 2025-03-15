"""
Script Parser Module.

This module provides functionality for parsing markdown-formatted audio drama scripts
and extracting structured information for the audio drama generator.
"""

from pathlib import Path
import logging
from typing import Dict, List, Any, Optional

from .script_parser import ScriptParser
from .markdown_parser import MarkdownParser
from .character_extractor import CharacterExtractor
from .sound_cue_extractor import SoundCueExtractor
from .script_structure_builder import ScriptStructureBuilder

__version__ = '0.1.0'

# Setup logging
logger = logging.getLogger(__name__)

def parse_script(script_path: str, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
  """
  Parse a markdown script file and return a structured representation.

  Args:
      script_path (str): Path to the markdown script file
      config (dict, optional): Configuration options

  Returns:
      dict: Structured script data
  """
  parser = ScriptParser(config)
  return parser.parse_script(script_path)

def extract_characters(script_content: str, config: Optional[Dict[str, Any]] = None) -> Dict[str, Dict[str, Any]]:
  """
  Extract character information from script content.

  Args:
      script_content (str): Script content
      config (dict, optional): Configuration options

  Returns:
      dict: Character information
  """
  extractor = CharacterExtractor(config)
  return extractor.extract_characters(script_content)

def extract_sound_cues(script_content: str, config: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
  """
  Extract sound cues from script content.

  Args:
      script_content (str): Script content
      config (dict, optional): Configuration options

  Returns:
      list: Sound cues
  """
  extractor = SoundCueExtractor(config)
  return extractor.extract_sound_cues(script_content)

def build_script_structure(
    metadata: Dict[str, str],
    characters: Dict[str, Dict[str, Any]],
    scenes: List[Dict[str, Any]],
    sound_cues: List[Dict[str, Any]],
    special_treatments: Optional[List[Dict[str, Any]]] = None,
    config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
  """
  Build a unified script structure with timing information.

  Args:
      metadata (dict): Script metadata
      characters (dict): Character information
      scenes (list): Scene information
      sound_cues (list): Sound cues
      special_treatments (list, optional): Special sound treatments
      config (dict, optional): Configuration options

  Returns:
      dict: Unified script structure
  """
  builder = ScriptStructureBuilder(config)
  return builder.build_script_structure(
    metadata, characters, scenes, sound_cues, special_treatments
  )

def save_script_structure(script_structure: Dict[str, Any], output_path: str) -> None:
  """
  Save script structure to a JSON file.

  Args:
      script_structure (dict): Script structure
      output_path (str): Output file path
  """
  builder = ScriptStructureBuilder()
  builder.save_script_structure(script_structure, output_path)

def load_script_structure(input_path: str) -> Dict[str, Any]:
  """
  Load script structure from a JSON file.

  Args:
      input_path (str): Input file path

  Returns:
      dict: Loaded script structure
  """
  builder = ScriptStructureBuilder()
  return builder.load_script_structure(input_path)