"""
Unit tests for the configuration loader.
"""

import os
import tempfile
import unittest
from pathlib import Path
import yaml

# Import the module to test
import sys
sys.path.append(str(Path(__file__).parent.parent.parent))
from utils.config_loader import load_config, validate_config, get_config_value

class TestConfigLoader(unittest.TestCase):
  """Tests for the configuration loader."""

  def setUp(self):
    """Set up the test environment."""
    # Create a temporary config file
    self.temp_dir = tempfile.TemporaryDirectory()
    self.config_path = Path(self.temp_dir.name) / "test_config.yaml"

    # Sample valid configuration
    self.valid_config = {
      "general": {
        "audio": {
          "sample_rate": 44100
        },
        "directories": {
          "output": "test_output"
        }
      },
      "script_parser": {
        "character": {
          "extract_voice_traits": True
        }
      },
      "voice_generator": {
        "models": {
          "tts_model": "test_model"
        }
      },
      "sound_manager": {
        "library": {
          "enable_search": True
        }
      },
      "audio_mixer": {
        "mixing": {
          "dialogue_level": 0.0
        }
      }
    }

    # Write the valid config to a file
    with open(self.config_path, 'w') as f:
      yaml.dump(self.valid_config, f)

  def tearDown(self):
    """Clean up the test environment."""
    self.temp_dir.cleanup()

  def test_load_config(self):
    """Test loading a configuration file."""
    config = load_config(self.config_path)
    self.assertEqual(config["general"]["audio"]["sample_rate"], 44100)
    self.assertEqual(config["voice_generator"]["models"]["tts_model"], "test_model")

  def test_load_config_not_found(self):
    """Test loading a non-existent configuration file."""
    with self.assertRaises(FileNotFoundError):
      load_config("non_existent_config.yaml")

  def test_load_config_invalid_yaml(self):
    """Test loading a configuration file with invalid YAML."""
    # Create an invalid YAML file
    invalid_path = Path(self.temp_dir.name) / "invalid_config.yaml"
    with open(invalid_path, 'w') as f:
      f.write("invalid: yaml: test:\n  - missing: colon\n")

    with self.assertRaises(yaml.YAMLError):
      load_config(invalid_path)

  def test_validate_config(self):
    """Test validating a configuration."""
    # Valid config
    self.assertTrue(validate_config(self.valid_config))

    # Missing required section
    invalid_config = self.valid_config.copy()
    del invalid_config["voice_generator"]
    self.assertFalse(validate_config(invalid_config))

  def test_get_config_value(self):
    """Test getting a value from the configuration."""
    # Existing value
    value = get_config_value(self.valid_config, "general.audio.sample_rate")
    self.assertEqual(value, 44100)

    # Non-existent value, with default
    value = get_config_value(self.valid_config, "non.existent.key", "default_value")
    self.assertEqual(value, "default_value")

    # Non-existent value, without default (should return None)
    value = get_config_value(self.valid_config, "non.existent.key")
    self.assertIsNone(value)

    # Nested values
    value = get_config_value(self.valid_config, "script_parser.character.extract_voice_traits")
    self.assertTrue(value)

if __name__ == "__main__":
  unittest.main()