#!/usr/bin/env python3
"""
Unit tests for the voice generator module.
"""

import os
import json
import unittest
from pathlib import Path
import tempfile
import numpy as np

# Add parent directory to path for imports
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from voice_generator.voice_profiles import (
  generate_character_voice_profile,
  voice_traits_to_parameters,
  create_voice_profile
)

class TestVoiceProfiles(unittest.TestCase):
  """Tests for voice profile generation."""

  def test_voice_traits_to_parameters(self):
    """Test converting voice traits to parameters."""
    # Test with empty traits
    params = voice_traits_to_parameters([])
    self.assertIsInstance(params, dict)
    self.assertEqual(params["pitch"], 0)
    self.assertEqual(params["speed"], 1.0)

    # Test with single trait
    params = voice_traits_to_parameters(["deep"])
    self.assertLess(params["pitch"], 0)  # Deep voice should have negative pitch

    # Test with multiple traits
    params = voice_traits_to_parameters(["deep", "slow", "gravelly"])
    self.assertLess(params["pitch"], 0)  # Deep voice should have negative pitch
    self.assertLess(params["speed"], 1.0)  # Slow voice should have speed < 1.0
    self.assertIn("distortion", params["effects"])  # Gravelly should add distortion effect

    # Test with conflicting traits
    params = voice_traits_to_parameters(["deep", "high"])
    # The parameters should be additively combined
    self.assertNotEqual(params["pitch"], 0)

  def test_create_voice_profile(self):
    """Test creating a voice profile."""
    # Test with default base profile
    profile = create_voice_profile()
    self.assertIsInstance(profile, dict)
    self.assertEqual(profile["gender"], "neutral")

    # Test with specific base profile
    profile = create_voice_profile("male_deep")
    self.assertIsInstance(profile, dict)
    self.assertEqual(profile["gender"], "male")
    self.assertLess(profile["pitch"], 0)  # Male deep should have negative pitch

    # Test with base profile and traits
    profile = create_voice_profile("neutral", ["happy", "fast"])
    self.assertIsInstance(profile, dict)
    self.assertGreater(profile["speed"], 1.0)  # Fast should have speed > 1.0
    self.assertGreater(profile["pitch"], 0)  # Happy should have positive pitch

  def test_generate_character_voice_profile(self):
    """Test generating a character voice profile."""
    # Test with male traits
    traits = ["deep", "gravelly", "middle-aged", "rural", "deliberate"]
    profile = generate_character_voice_profile(traits)
    self.assertIsInstance(profile, dict)
    self.assertEqual(profile["gender"], "male")
    self.assertLess(profile["pitch"], 0)
    self.assertLess(profile["speed"], 1.0)
    self.assertIn("effects", profile)

    # Test with female traits
    traits = ["high", "melodic", "seductive", "light"]
    profile = generate_character_voice_profile(traits)
    self.assertIsInstance(profile, dict)
    self.assertEqual(profile["gender"], "female")
    self.assertGreater(profile["pitch"], 0)

    # Test with narrator traits
    traits = ["neutral", "clear", "measured", "slightly-ominous", "observant"]
    profile = generate_character_voice_profile(traits)
    self.assertIsInstance(profile, dict)
    self.assertIn("effects", profile)

    # Test with child voice
    traits = ["child", "high", "fast"]
    profile = generate_character_voice_profile(traits)
    self.assertIsInstance(profile, dict)
    self.assertGreater(profile["pitch"], 5)  # Child voice should have high pitch


# Only run effect tests if libraries are available
try:
  import librosa
  import scipy
  RUN_EFFECT_TESTS = True
except ImportError:
  RUN_EFFECT_TESTS = False

@unittest.skipIf(not RUN_EFFECT_TESTS, "Audio libraries not available")
class TestVoiceEffects(unittest.TestCase):
  """Tests for voice effects."""

  def setUp(self):
    """Set up for voice effect tests."""
    from voice_generator.effects import (
      apply_reverb,
      apply_echo,
      apply_pitch_shift,
      apply_timestretch,
      apply_effect_chain
    )

    self.apply_reverb = apply_reverb
    self.apply_echo = apply_echo
    self.apply_pitch_shift = apply_pitch_shift
    self.apply_timestretch = apply_timestretch
    self.apply_effect_chain = apply_effect_chain

    # Create a simple test signal (sine wave)
    self.sample_rate = 22050
    duration = 1.0  # seconds
    t = np.linspace(0, duration, int(self.sample_rate * duration), endpoint=False)
    self.test_audio = 0.5 * np.sin(2 * np.pi * 440 * t)  # 440 Hz sine wave

  def test_apply_reverb(self):
    """Test applying reverb effect."""
    result = self.apply_reverb(self.test_audio, room_size=0.5, sample_rate=self.sample_rate)
    self.assertIsInstance(result, np.ndarray)
    self.assertEqual(len(result), len(self.test_audio))

    # Reverb should make the signal longer or equal (but we truncate it)
    energy_before = np.sum(self.test_audio ** 2)
    energy_after = np.sum(result ** 2)
    self.assertGreaterEqual(energy_after, energy_before * 0.9)  # Allow for some energy loss due to filtering

  def test_apply_echo(self):
    """Test applying echo effect."""
    result = self.apply_echo(self.test_audio, delay=0.2, decay=0.5, sample_rate=self.sample_rate)
    self.assertIsInstance(result, np.ndarray)
    self.assertEqual(len(result), len(self.test_audio))

    # Echo should add energy to the signal
    energy_before = np.sum(self.test_audio ** 2)
    energy_after = np.sum(result ** 2)
    self.assertGreater(energy_after, energy_before)

  def test_apply_pitch_shift(self):
    """Test applying pitch shift effect."""
    # Shift up
    result_up = self.apply_pitch_shift(self.test_audio, semitones=2.0, sample_rate=self.sample_rate)
    self.assertIsInstance(result_up, np.ndarray)
    self.assertEqual(len(result_up), len(self.test_audio))

    # Shift down
    result_down = self.apply_pitch_shift(self.test_audio, semitones=-2.0, sample_rate=self.sample_rate)
    self.assertIsInstance(result_down, np.ndarray)
    self.assertEqual(len(result_down), len(self.test_audio))

    # No shift should return similar signal
    result_none = self.apply_pitch_shift(self.test_audio, semitones=0.0, sample_rate=self.sample_rate)
    self.assertIsInstance(result_none, np.ndarray)
    self.assertEqual(len(result_none), len(self.test_audio))
    np.testing.assert_allclose(result_none, self.test_audio, rtol=1e-2, atol=1e-2)

  def test_apply_timestretch(self):
    """Test applying time stretch effect."""
    # Faster
    result_faster = self.apply_timestretch(self.test_audio, rate=1.2, sample_rate=self.sample_rate)
    self.assertIsInstance(result_faster, np.ndarray)

    # Slower
    result_slower = self.apply_timestretch(self.test_audio, rate=0.8, sample_rate=self.sample_rate)
    self.assertIsInstance(result_slower, np.ndarray)

    # No stretch should return similar signal
    result_none = self.apply_timestretch(self.test_audio, rate=1.0, sample_rate=self.sample_rate)
    self.assertIsInstance(result_none, np.ndarray)
    self.assertEqual(len(result_none), len(self.test_audio))
    np.testing.assert_allclose(result_none, self.test_audio, rtol=1e-2, atol=1e-2)

  def test_apply_effect_chain(self):
    """Test applying a chain of effects."""
    effects = {
      "reverb": {"room_size": 0.5, "damping": 0.5},
      "echo": {"delay": 0.3, "decay": 0.5}
    }

    result = self.apply_effect_chain(self.test_audio, effects, sample_rate=self.sample_rate)
    self.assertIsInstance(result, np.ndarray)

    # Empty effects should return original signal
    result_none = self.apply_effect_chain(self.test_audio, {}, sample_rate=self.sample_rate)
    self.assertIsInstance(result_none, np.ndarray)
    np.testing.assert_array_equal(result_none, self.test_audio)


# Skip the full generator tests since they require downloading models
@unittest.skip("These tests require downloading models")
class TestVoiceGenerator(unittest.TestCase):
  """Tests for the full voice generator."""

  def setUp(self):
    """Set up for voice generator tests."""
    import tempfile
    from utils.config_loader import load_config
    from voice_generator.voice_generator import VoiceGenerator, initialize_voice_models

    self.config = load_config()
    self.voice_config = self.config.get("voice_generator", {})
    self.temp_dir = tempfile.TemporaryDirectory()
    self.output_dir = self.temp_dir.name

  def tearDown(self):
    """Clean up after tests."""
    self.temp_dir.cleanup()

  def test_initialize_voice_models(self):
    """Test initializing voice models."""
    from voice_generator.voice_generator import initialize_voice_models

    # This will download models if not already available
    generator = initialize_voice_models(self.config, use_gpu=False)
    self.assertIsNotNone(generator)
    self.assertIsInstance(generator.device, torch.device)

  def test_generate_voice_clip(self):
    """Test generating a voice clip."""
    from voice_generator.voice_generator import initialize_voice_models

    # Initialize generator
    generator = initialize_voice_models(self.config, use_gpu=False)

    # Create a simple voice profile
    voice_profile = create_voice_profile("neutral")

    # Generate a voice clip
    text = "This is a test of the voice generator."
    output_path = os.path.join(self.output_dir, "test_voice.wav")

    generator.generate_voice_clip(text, voice_profile, output_path=output_path)

    # Check that the file was created
    self.assertTrue(os.path.exists(output_path))
    self.assertGreater(os.path.getsize(output_path), 1000)  # Should be a valid audio file

  def test_generate_character_voices(self):
    """Test generating voices for all characters in a script."""
    from voice_generator.voice_generator import initialize_voice_models

    # Initialize generator
    generator = initialize_voice_models(self.config, use_gpu=False)

    # Create a simple script with characters
    script_data = {
      "characters": {
        "NARRATOR": {
          "voice_traits": ["neutral", "clear", "measured"]
        },
        "THOMAS": {
          "voice_traits": ["deep", "gravelly", "middle-aged", "rural", "deliberate"]
        },
        "DIANE": {
          "voice_traits": ["warm", "melodic", "seductive", "light"]
        }
      }
    }

    # Generate voices
    character_voices = generator.generate_character_voices(script_data, self.output_dir)

    # Check results
    self.assertIsInstance(character_voices, dict)
    self.assertGreaterEqual(len(character_voices), 2)  # Should have at least 2 characters

    # Check that files were created
    for char_code, char_data in character_voices.items():
      self.assertIn("profile", char_data)
      self.assertIn("sample_path", char_data)

      if char_data["sample_path"]:
        self.assertTrue(os.path.exists(char_data["sample_path"]))
        self.assertGreater(os.path.getsize(char_data["sample_path"]), 1000)


if __name__ == "__main__":
  unittest.main()