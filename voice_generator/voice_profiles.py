#!/usr/bin/env python3
"""
Voice profile generation for the Automated Audio Drama Generator.

This module handles the creation of voice profiles based on character descriptions.
"""

import os
import json
import logging
import random
import numpy as np
from typing import Dict, List, Any, Optional, Tuple, Union

# Set up logging
logging.basicConfig(
  level=logging.INFO,
  format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Voice trait mappings
VOICE_TRAIT_MAPPINGS = {
  # Pitch-related traits
  "deep": {"pitch": -6, "pitch_range": 0.7, "formant_shift": -0.3},
  "low": {"pitch": -4, "pitch_range": 0.8, "formant_shift": -0.2},
  "baritone": {"pitch": -3, "formant_shift": -0.15},
  "bass": {"pitch": -5, "pitch_range": 0.7, "formant_shift": -0.25},
  "mid-range": {"pitch": 0, "pitch_range": 1.0},
  "medium": {"pitch": 0, "pitch_range": 1.0},
  "high": {"pitch": 3, "pitch_range": 1.2, "formant_shift": 0.2},
  "higher": {"pitch": 4, "pitch_range": 1.3, "formant_shift": 0.3},
  "soprano": {"pitch": 6, "pitch_range": 1.4, "formant_shift": 0.4},

  # Speed-related traits
  "slow": {"speed": 0.85},
  "deliberate": {"speed": 0.9},
  "measured": {"speed": 0.95},
  "normal": {"speed": 1.0},
  "fast": {"speed": 1.15},
  "fast-talking": {"speed": 1.2},
  "rapid": {"speed": 1.25},

  # Tone quality traits
  "gravelly": {"effects": {"distortion": {"amount": 0.1}}},
  "rough": {"effects": {"distortion": {"amount": 0.08}}},
  "smooth": {"effects": {"lowpass": {"cutoff": 0.8}}},
  "raspy": {
    "effects": {
      "distortion": {"amount": 0.15},
      "highpass": {"cutoff": 0.3}
    }
  },
  "breathy": {
    "effects": {
      "noise": {"amount": 0.05},
      "lowpass": {"cutoff": 0.7}
    }
  },
  "warm": {"formant_shift": 0.1, "effects": {"lowpass": {"cutoff": 0.75}}},
  "bright": {"formant_shift": 0.2, "effects": {"highpass": {"cutoff": 0.2}}},
  "dark": {"formant_shift": -0.2, "effects": {"lowpass": {"cutoff": 0.6}}},
  "resonant": {"effects": {"reverb": {"room_size": 0.3, "damping": 0.5}}},
  "melodic": {"pitch_range": 1.3},
  "monotone": {"pitch_range": 0.6},

  # Character and personality traits
  "confident": {"volume": 1.2, "speed": 1.05},
  "nervous": {
    "speed": 1.1,
    "pitch_range": 1.2,
    "effects": {"tremolo": {"depth": 0.05, "rate": 4.0}}
  },
  "shy": {"volume": 0.9, "speed": 0.95},
  "authoritative": {"volume": 1.15, "pitch": -2},
  "friendly": {"pitch_range": 1.1, "speed": 1.05},
  "threatening": {"pitch": -2, "effects": {"distortion": {"amount": 0.05}}},
  "gentle": {"volume": 0.9, "speed": 0.95},
  "harsh": {"volume": 1.1, "effects": {"highpass": {"cutoff": 0.3}}},
  "sarcastic": {"pitch_range": 1.3},
  "jovial": {"pitch": 1, "pitch_range": 1.2, "speed": 1.1},
  "serious": {"pitch": -1, "pitch_range": 0.8, "speed": 0.95},
  "anxious": {
    "speed": 1.1,
    "pitch_range": 1.15,
    "effects": {"tremolo": {"depth": 0.04, "rate": 5.0}}
  },
  "sad": {"pitch": -1, "speed": 0.9, "pitch_range": 0.8},
  "happy": {"pitch": 1, "speed": 1.05, "pitch_range": 1.1},
  "angry": {"pitch": -1, "volume": 1.2, "effects": {"distortion": {"amount": 0.05}}},
  "cheerful": {"pitch": 2, "speed": 1.1, "pitch_range": 1.2},
  "depressed": {"pitch": -2, "speed": 0.85, "pitch_range": 0.7},
  "excited": {"pitch": 2, "speed": 1.15, "pitch_range": 1.3, "volume": 1.15},
  "bored": {"pitch": -1, "speed": 0.9, "pitch_range": 0.7},

  # Age-related traits
  "child": {"pitch": 8, "formant_shift": 0.5, "pitch_range": 1.3},
  "young": {"pitch": 3, "formant_shift": 0.2, "speed": 1.05},
  "teenage": {"pitch": 2, "formant_shift": 0.1, "speed": 1.1},
  "middle-aged": {"pitch": 0, "formant_shift": 0},
  "old": {"pitch": -2, "formant_shift": -0.1, "speed": 0.9},
  "elderly": {"pitch": -3, "formant_shift": -0.15, "speed": 0.85},
  "ancient": {"pitch": -4, "formant_shift": -0.2, "speed": 0.8},

  # Accent/geographic traits
  "rural": {"effects": {"reverb": {"room_size": 0.2, "damping": 0.7}}},
  "urban": {"speed": 1.05},
  "southern": {"pitch": -1, "speed": 0.9},
  "northern": {"pitch": 1, "speed": 1.05},
  "western": {"pitch": -1},
  "eastern": {"pitch": 1},
  "british": {"effects": {"eq": {"high": 1.2}}},
  "american": {},
  "city-accent": {"speed": 1.1, "pitch_range": 1.1},
  "country-accent": {"speed": 0.95, "pitch": -1},
  "local-accent": {"speed": 0.97},

  # Modification traits
  "whispering": {
    "volume": 0.7,
    "effects": {
      "noise": {"amount": 0.1},
      "lowpass": {"cutoff": 0.6}
    }
  },
  "shouting": {"volume": 1.3, "effects": {"distortion": {"amount": 0.05}}},
  "nasal": {"formant_shift": 0.3, "effects": {"bandpass": {"center": 0.6, "q": 0.5}}},
  "hoarse": {"effects": {"distortion": {"amount": 0.12}, "lowpass": {"cutoff": 0.7}}},
  "trembling": {"effects": {"tremolo": {"depth": 0.1, "rate": 6.0}}},
  "robotic": {"effects": {"vocoder": {"bands": 16}}},
  "distant": {"volume": 0.8, "effects": {"reverb": {"room_size": 0.7, "damping": 0.5}}},
  "close": {"volume": 1.1},
  "ethereal": {"effects": {"reverb": {"room_size": 0.9, "damping": 0.3}}},

  # Special character traits
  "narrator": {"clarity": 1.2},
  "seductive": {"speed": 0.9, "pitch_range": 1.1, "volume": 0.9},
  "commanding": {"volume": 1.2, "pitch": -2},
  "timid": {"volume": 0.8, "speed": 0.95},
  "stuttering": {"effects": {"stutter": {"amount": 0.2}}},
  "mysterious": {"effects": {"reverb": {"room_size": 0.5, "damping": 0.6}}},
  "ominous": {"pitch": -3, "speed": 0.9, "effects": {"reverb": {"room_size": 0.6}}},
  "frightened": {
    "speed": 1.1,
    "pitch": 2,
    "effects": {"tremolo": {"depth": 0.08, "rate": 7.0}}
  },
  "wise": {"pitch": -1, "speed": 0.9},
  "cheerful": {"pitch": 2, "speed": 1.1},
  "manipulative": {"pitch_range": 1.2},
  "observant": {"clarity": 1.1},
  "slightly-ominous": {"pitch": -1, "effects": {"reverb": {"room_size": 0.3}}},
  "controlling": {"volume": 1.1, "pitch": -1},
  "weathered": {"effects": {"distortion": {"amount": 0.06}}},
  "absent": {"effects": {"reverb": {"room_size": 0.4}}}
}

# Base voice profiles
BASE_VOICE_PROFILES = {
  "male_deep": {
    "name": "Male Deep",
    "gender": "male",
    "pitch": -4,
    "pitch_range": 0.8,
    "formant_shift": -0.2,
    "speed": 1.0,
    "volume": 1.0,
    "clarity": 1.0,
    "speaker_id": "male_deep",
    "effects": {}
  },
  "male_medium": {
    "name": "Male Medium",
    "gender": "male",
    "pitch": -2,
    "pitch_range": 0.9,
    "formant_shift": -0.1,
    "speed": 1.0,
    "volume": 1.0,
    "clarity": 1.0,
    "speaker_id": "male_medium",
    "effects": {}
  },
  "male_light": {
    "name": "Male Light",
    "gender": "male",
    "pitch": 0,
    "pitch_range": 1.0,
    "formant_shift": 0.0,
    "speed": 1.0,
    "volume": 1.0,
    "clarity": 1.0,
    "speaker_id": "male_light",
    "effects": {}
  },
  "female_deep": {
    "name": "Female Deep",
    "gender": "female",
    "pitch": 0,
    "pitch_range": 1.0,
    "formant_shift": 0.0,
    "speed": 1.0,
    "volume": 1.0,
    "clarity": 1.0,
    "speaker_id": "female_deep",
    "effects": {}
  },
  "female_medium": {
    "name": "Female Medium",
    "gender": "female",
    "pitch": 2,
    "pitch_range": 1.1,
    "formant_shift": 0.1,
    "speed": 1.0,
    "volume": 1.0,
    "clarity": 1.0,
    "speaker_id": "female_medium",
    "effects": {}
  },
  "female_light": {
    "name": "Female Light",
    "gender": "female",
    "pitch": 4,
    "pitch_range": 1.2,
    "formant_shift": 0.2,
    "speed": 1.0,
    "volume": 1.0,
    "clarity": 1.0,
    "speaker_id": "female_light",
    "effects": {}
  },
  "neutral": {
    "name": "Neutral",
    "gender": "neutral",
    "pitch": 0,
    "pitch_range": 1.0,
    "formant_shift": 0.0,
    "speed": 1.0,
    "volume": 1.0,
    "clarity": 1.0,
    "speaker_id": "neutral",
    "effects": {}
  },
  "child": {
    "name": "Child",
    "gender": "neutral",
    "pitch": 6,
    "pitch_range": 1.3,
    "formant_shift": 0.4,
    "speed": 1.1,
    "volume": 1.0,
    "clarity": 1.0,
    "speaker_id": "child",
    "effects": {}
  },
  "elder": {
    "name": "Elder",
    "gender": "neutral",
    "pitch": -3,
    "pitch_range": 0.8,
    "formant_shift": -0.15,
    "speed": 0.9,
    "volume": 0.9,
    "clarity": 0.9,
    "speaker_id": "elder",
    "effects": {
      "tremolo": {"depth": 0.03, "rate": 5.0}
    }
  }
}

def voice_traits_to_parameters(voice_traits: List[str]) -> Dict[str, Any]:
  """
  Convert voice trait descriptors to voice generation parameters.

  Args:
      voice_traits: List of descriptive voice traits

  Returns:
      Dictionary of voice parameters
  """
  # Initialize with default parameters
  parameters = {
    "pitch": 0,           # Semitones, 0 = neutral, -12 to 12 typical range
    "pitch_range": 1.0,   # Multiplier for pitch variation, 0.7-1.4 typical range
    "formant_shift": 0.0, # Shift formants to adjust voice "character"
    "speed": 1.0,         # Speed multiplier, 0.8-1.2 typical range
    "volume": 1.0,        # Volume level, 0.6-1.3 typical range
    "clarity": 1.0,       # Voice clarity, affects articulation
    "speaker_id": None,   # Specific speaker ID if using a multi-speaker model
    "gender": "neutral",  # Voice gender characteristic
    "effects": {}         # Audio effects to apply
  }

  # Apply each trait's effect from the mappings
  for trait in voice_traits:
    trait = trait.lower()
    if trait in VOICE_TRAIT_MAPPINGS:
      trait_params = VOICE_TRAIT_MAPPINGS[trait]

      # Apply each parameter from the trait
      for param, value in trait_params.items():
        if param == "effects":
          # Merge effects dictionaries
          for effect_name, effect_params in value.items():
            parameters["effects"][effect_name] = effect_params
        else:
          # For numerical parameters, we add the values (allowing positive/negative adjustments)
          if isinstance(value, (int, float)) and param in parameters and isinstance(parameters[param], (int, float)):
            parameters[param] += value
          else:
            # For other parameters, we replace the value
            parameters[param] = value

  # Infer gender if not explicitly set
  if parameters["gender"] == "neutral":
    # Guess gender based on pitch and formant
    if parameters["pitch"] < -2 or parameters["formant_shift"] < -0.1:
      parameters["gender"] = "male"
    elif parameters["pitch"] > 2 or parameters["formant_shift"] > 0.1:
      parameters["gender"] = "female"

  # Infer speaker_id if not set based on gender and pitch
  if parameters["speaker_id"] is None:
    if parameters["gender"] == "male":
      if parameters["pitch"] < -3:
        parameters["speaker_id"] = "male_deep"
      elif parameters["pitch"] < 0:
        parameters["speaker_id"] = "male_medium"
      else:
        parameters["speaker_id"] = "male_light"
    elif parameters["gender"] == "female":
      if parameters["pitch"] < 1:
        parameters["speaker_id"] = "female_deep"
      elif parameters["pitch"] < 3:
        parameters["speaker_id"] = "female_medium"
      else:
        parameters["speaker_id"] = "female_light"
    else:
      parameters["speaker_id"] = "neutral"

  # Ensure parameters are within reasonable ranges
  parameters["pitch"] = max(-12, min(12, parameters["pitch"]))
  parameters["pitch_range"] = max(0.6, min(1.5, parameters["pitch_range"]))
  parameters["formant_shift"] = max(-0.5, min(0.5, parameters["formant_shift"]))
  parameters["speed"] = max(0.7, min(1.3, parameters["speed"]))
  parameters["volume"] = max(0.6, min(1.3, parameters["volume"]))
  parameters["clarity"] = max(0.7, min(1.3, parameters["clarity"]))

  return parameters


def create_voice_profile(base_profile_type: str = "neutral", voice_traits: Optional[List[str]] = None) -> Dict[str, Any]:
  """
  Create a voice profile based on a base profile type and optional traits.

  Args:
      base_profile_type: Base profile type to start with
      voice_traits: List of voice traits to apply (optional)

  Returns:
      Complete voice profile dictionary
  """
  # Get the base profile
  if base_profile_type in BASE_VOICE_PROFILES:
    profile = BASE_VOICE_PROFILES[base_profile_type].copy()
  else:
    profile = BASE_VOICE_PROFILES["neutral"].copy()

  # Apply voice traits if provided
  if voice_traits:
    trait_params = voice_traits_to_parameters(voice_traits)

    # Update profile with trait parameters
    for key, value in trait_params.items():
      if key == "effects":
        # Merge effects dictionaries
        if "effects" not in profile:
          profile["effects"] = {}
        for effect_name, effect_params in value.items():
          profile["effects"][effect_name] = effect_params
      else:
        profile[key] = value

  return profile


def generate_character_voice_profile(voice_traits: List[str]) -> Dict[str, Any]:
  """
  Generate a voice profile for a character based on descriptive traits.

  Args:
      voice_traits: List of descriptive voice traits

  Returns:
      Voice profile dictionary
  """
  # Determine the most likely base profile from traits
  base_profile = "neutral"

  gender_related_traits = {"male", "female", "man", "woman", "boy", "girl", "masculine", "feminine"}
  age_related_traits = {"child", "young", "teenage", "middle-aged", "old", "elderly", "ancient"}

  # Check for gender traits
  gender_match = False
  for trait in voice_traits:
    trait_lower = trait.lower()
    if trait_lower in gender_related_traits:
      gender_match = True
      if trait_lower in {"male", "man", "boy", "masculine"}:
        if "deep" in voice_traits or "low" in voice_traits:
          base_profile = "male_deep"
        elif "high" in voice_traits or "light" in voice_traits:
          base_profile = "male_light"
        else:
          base_profile = "male_medium"
      elif trait_lower in {"female", "woman", "girl", "feminine"}:
        if "deep" in voice_traits or "low" in voice_traits:
          base_profile = "female_deep"
        elif "high" in voice_traits or "light" in voice_traits:
          base_profile = "female_light"
        else:
          base_profile = "female_medium"

  # If no explicit gender, infer from other traits
  if not gender_match:
    male_indicators = {"deep", "baritone", "gravelly", "rough"}
    female_indicators = {"soprano", "high", "light", "breathy"}

    male_count = sum(1 for trait in voice_traits if trait.lower() in male_indicators)
    female_count = sum(1 for trait in voice_traits if trait.lower() in female_indicators)

    if male_count > female_count:
      base_profile = "male_medium"
    elif female_count > male_count:
      base_profile = "female_medium"

  # Check for age traits
  for trait in voice_traits:
    trait_lower = trait.lower()
    if trait_lower in age_related_traits:
      if trait_lower == "child":
        base_profile = "child"
      elif trait_lower in {"elderly", "ancient", "old"}:
        base_profile = "elder"

  # Create the profile
  return create_voice_profile(base_profile, voice_traits)