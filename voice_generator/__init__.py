"""
Voice Generator Module.

This module provides functionality for generating character voices
based on script descriptions and applying voice effects.
"""

from .voice_generator import (
  generate_voices,
  generate_voice_clip,
  apply_voice_effect,
  initialize_voice_models,
  load_voice_profile,
  save_voice_profile,
  VoiceGenerator
)

from .voice_profiles import (
  create_voice_profile,
  generate_character_voice_profile,
  voice_traits_to_parameters
)

from .effects import (
  apply_reverb,
  apply_echo,
  apply_pitch_shift,
  apply_timestretch,
  apply_effect_chain
)

__version__ = '0.1.0'

__all__ = [
  'generate_voices',
  'generate_voice_clip',
  'apply_voice_effect',
  'initialize_voice_models',
  'load_voice_profile',
  'save_voice_profile',
  'VoiceGenerator',
  'create_voice_profile',
  'generate_character_voice_profile',
  'voice_traits_to_parameters',
  'apply_reverb',
  'apply_echo',
  'apply_pitch_shift',
  'apply_timestretch',
  'apply_effect_chain'
]