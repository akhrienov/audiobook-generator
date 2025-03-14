"""
Configuration loader for the Automated Audio Drama Generator.

This module provides functions for loading and validating configuration files.
"""

import os
import sys
import logging
import yaml
from pathlib import Path
from typing import Dict, Any, Optional

# Setup logging
logger = logging.getLogger(__name__)

# Default configuration file path
DEFAULT_CONFIG_PATH = Path(__file__).parent.parent / "config.yaml"

def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
  """
  Load configuration from a YAML file.

  Args:
      config_path (str, optional): Path to the configuration file.
          If None, the default configuration will be used.

  Returns:
      dict: Configuration dictionary

  Raises:
      FileNotFoundError: If the configuration file doesn't exist
      yaml.YAMLError: If the configuration file has invalid YAML syntax
  """
  # Use default config if not specified
  if config_path is None:
    config_path = DEFAULT_CONFIG_PATH
  else:
    config_path = Path(config_path)

  logger.info(f"Loading configuration from {config_path}")

  # Check if the file exists
  if not config_path.exists():
    logger.error(f"Configuration file not found: {config_path}")
    raise FileNotFoundError(f"Configuration file not found: {config_path}")

  # Load the configuration
  try:
    with open(config_path, 'r') as f:
      config = yaml.safe_load(f)

    logger.info("Configuration loaded successfully")
    return config
  except yaml.YAMLError as e:
    logger.error(f"Error parsing configuration file: {e}")
    raise
  except Exception as e:
    logger.error(f"Error loading configuration: {e}")
    raise

def validate_config(config: Dict[str, Any]) -> bool:
  """
  Validate the configuration.

  Args:
      config (dict): Configuration dictionary

  Returns:
      bool: True if the configuration is valid, False otherwise
  """
  # Check for required sections
  required_sections = [
    "general",
    "script_parser",
    "voice_generator",
    "sound_manager",
    "audio_mixer"
  ]

  # Check for missing sections
  missing_sections = [section for section in required_sections if section not in config]
  if missing_sections:
    logger.error(f"Missing configuration sections: {', '.join(missing_sections)}")
    return False

  # Additional validation could be added here

  logger.info("Configuration validation successful")
  return True

def get_config_value(config: Dict[str, Any], key_path: str, default: Any = None) -> Any:
  """
  Get a value from the configuration using a dot-separated path.

  Args:
      config (dict): Configuration dictionary
      key_path (str): Dot-separated path to the configuration value
      default (any, optional): Default value if the key doesn't exist

  Returns:
      any: The configuration value or the default value
  """
  keys = key_path.split(".")
  value = config

  for key in keys:
    if isinstance(value, dict) and key in value:
      value = value[key]
    else:
      logger.warning(f"Configuration key not found: {key_path}")
      return default

  return value

def create_directories(config: Dict[str, Any]) -> None:
  """
  Create directories specified in the configuration.

  Args:
      config (dict): Configuration dictionary
  """
  directories = get_config_value(config, "general.directories", {})

  for name, path in directories.items():
    dir_path = Path(path)
    if not dir_path.exists():
      logger.info(f"Creating directory: {dir_path}")
      dir_path.mkdir(parents=True, exist_ok=True)

def setup_config(config_path: Optional[str] = None) -> Dict[str, Any]:
  """
  Load, validate, and set up the configuration.

  Args:
      config_path (str, optional): Path to the configuration file

  Returns:
      dict: Validated configuration dictionary
  """
  # Load the configuration
  config = load_config(config_path)

  # Validate the configuration
  if not validate_config(config):
    logger.error("Configuration validation failed")
    sys.exit(1)

  # Create required directories
  create_directories(config)

  return config