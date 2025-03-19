#!/usr/bin/env python3
"""
Voice Generator module for the Automated Audio Drama Generator.

This module handles the generation of character voices using TTS models from Hugging Face.
"""

import os
import json
import logging
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional

import torch
import torchaudio
import numpy as np
import soundfile as sf

# Import SpeechT5 directly since it's most commonly available
from transformers import SpeechT5Processor, SpeechT5ForTextToSpeech, SpeechT5HifiGan

from .voice_profiles import generate_character_voice_profile, voice_traits_to_parameters
from .effects import apply_effect_chain

# Set up logging
logging.basicConfig(
  level=logging.INFO,
  format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

class VoiceGenerator:
  """Class for handling voice generation for audio drama characters."""

  def __init__(self, config: Dict[str, Any], use_gpu: bool = True):
    """
    Initialize the voice generator.

    Args:
        config: Voice generator configuration
        use_gpu: Whether to use GPU for inference
    """
    self.config = config
    self.device = torch.device("cuda" if torch.cuda.is_available() and use_gpu else "cpu")
    logger.info(f"Using device: {self.device}")

    # Initialize state
    self.models = {}
    self.processors = {}
    self.vocoders = {}
    self.speaker_embeddings = {}

    # Load models based on config
    self._load_models()

  def _load_models(self):
    """Load the TTS models, processors, and vocoders."""
    models_config = self.config.get("models", {})

    # Load the text-to-speech model (default: SpeechT5)
    tts_model_id = models_config.get("tts_model", "microsoft/speecht5_tts")

    try:
      logger.info(f"Loading TTS model: {tts_model_id}")

      # For SpeechT5 models
      if "speecht5" in tts_model_id:
        self.processors["tts"] = SpeechT5Processor.from_pretrained(tts_model_id)
        self.models["tts"] = SpeechT5ForTextToSpeech.from_pretrained(tts_model_id).to(self.device)
      else:
        # For other models (general AutoModelForTextToSpeech)
        self.processors["tts"] = AutoProcessor.from_pretrained(tts_model_id)
        self.models["tts"] = AutoModelForTextToSpeech.from_pretrained(tts_model_id).to(self.device)

      # Load vocoder
      vocoder_model_id = models_config.get("vocoder_model", "facebook/vits-ljspeech")

      logger.info(f"Loading vocoder model: {vocoder_model_id}")
      if "speecht5" in tts_model_id:
        self.vocoders["default"] = SpeechT5HifiGan.from_pretrained("microsoft/speecht5_hifigan").to(self.device)
      else:
        # For other models, load appropriate vocoder
        self.vocoders["default"] = AutoModelForTextToSpeech.from_pretrained(vocoder_model_id).to(self.device)

      # Always load speaker embeddings for SpeechT5 models
      if "speecht5" in tts_model_id:
        self._load_speaker_embeddings()
      # Also load if explicitly configured
      elif models_config.get("preload_speakers", False):
        self._load_speaker_embeddings()

      logger.info("Models loaded successfully")

    except Exception as e:
      logger.error(f"Error loading models: {str(e)}")
      raise

  def _load_speaker_embeddings(self):
    """Load pre-computed speaker embeddings if available."""
    # Try different paths for speaker embeddings
    potential_paths = [
      Path(self.config.get("embeddings_directory",
                           self.config.get("directories", {}).get("embeddings", "models/embeddings"))),
      Path("models/embeddings"),
      Path("embeddings"),
      Path(__file__).parent.parent / "models" / "embeddings",
      ]

    # Find the first path that exists
    embeddings_dir = None
    for path in potential_paths:
      if path.exists():
        embeddings_dir = path
        break

    if not embeddings_dir:
      logger.warning(f"Speaker embeddings directory not found. Voice generation may fail.")
      return

    try:
      # Look for profile mappings first
      mapping_path = embeddings_dir / "profile_mappings.json"
      if mapping_path.exists():
        import json
        with open(mapping_path, 'r') as f:
          mappings = json.load(f)
        logger.info(f"Found voice profile mappings: {mapping_path}")

      # Load all .pt files in the directory
      embedding_count = 0
      for emb_file in embeddings_dir.glob("*.pt"):
        speaker_id = emb_file.stem
        logger.info(f"Loading speaker embedding: {speaker_id}")
        self.speaker_embeddings[speaker_id] = torch.load(emb_file, map_location=self.device)
        embedding_count += 1

      # Add mappings as aliases if we have them
      if 'mappings' in locals():
        for profile_name, embedding_file in mappings.items():
          # If the value is a file name, look up the loaded embedding
          if isinstance(embedding_file, str) and embedding_file.endswith('.pt'):
            embedding_key = Path(embedding_file).stem
            if embedding_key in self.speaker_embeddings and profile_name not in self.speaker_embeddings:
              self.speaker_embeddings[profile_name] = self.speaker_embeddings[embedding_key]
          # Otherwise, assume it's a direct speaker ID
          elif embedding_file in self.speaker_embeddings and profile_name not in self.speaker_embeddings:
            self.speaker_embeddings[profile_name] = self.speaker_embeddings[embedding_file]

      if embedding_count > 0:
        logger.info(f"Loaded {embedding_count} speaker embeddings from {embeddings_dir}")
      else:
        logger.warning(f"No speaker embeddings found in {embeddings_dir}")

    except Exception as e:
      logger.error(f"Error loading speaker embeddings: {str(e)}")
      logger.warning("Voice generation may fail. Run `python -m voice_generator.download_models --embeddings-only` to download speaker embeddings.")

  def generate_character_voices(self, script_data: Dict[str, Any], output_dir: Optional[str] = None) -> Dict[str, Dict[str, Any]]:
    """
    Generate voice profiles and audio samples for all characters in the script.

    Args:
        script_data: Parsed script data
        output_dir: Directory to save voice samples (optional)

    Returns:
        Dictionary mapping character codes to voice profiles and audio samples
    """
    characters = script_data.get("characters", {})

    if not characters:
      logger.warning("No characters found in script data")
      return {}

    # Create output directory if needed
    if output_dir:
      output_path = Path(output_dir)
      output_path.mkdir(parents=True, exist_ok=True)

    # Generate voice profiles for all characters
    result = {}

    for char_code, char_data in characters.items():
      logger.info(f"Generating voice for character: {char_code}")

      # Extract voice traits
      voice_traits = char_data.get("voice_traits", [])

      if not voice_traits:
        logger.warning(f"No voice traits specified for character {char_code}")
        continue

      try:
        # Generate voice profile
        voice_profile = generate_character_voice_profile(voice_traits)

        # Generate a sample voice clip for this character
        sample_text = f"Hello, my name is {char_code}."

        if "dialogue_sample" in char_data:
          sample_text = char_data["dialogue_sample"]

        # Generate sample audio
        audio_path = None
        if output_dir:
          audio_path = str(output_path / f"{char_code.lower()}_sample.wav")

        audio_data = self.generate_voice_clip(sample_text, voice_profile, output_path=audio_path)

        # Store the result
        result[char_code] = {
          "profile": voice_profile,
          "sample_path": audio_path,
          "sample_duration": len(audio_data) / self.config.get("audio", {}).get("sample_rate", 22050)
        }

        # Save voice profile
        if output_dir:
          profile_path = output_path / f"{char_code.lower()}_profile.json"
          save_voice_profile(voice_profile, str(profile_path))

      except Exception as e:
        logger.error(f"Error generating voice for character {char_code}: {str(e)}")

    return result

  def generate_voice_clip(self,
                          text: str,
                          voice_profile: Dict[str, Any],
                          emotion: Optional[str] = None,
                          output_path: Optional[str] = None) -> np.ndarray:
    """
    Generate a voice clip for the given text using the specified voice profile.

    Args:
        text: The text to convert to speech
        voice_profile: Voice parameters to use
        emotion: Emotional tone for the delivery (optional)
        output_path: Path to save the audio file (optional)

    Returns:
        Audio data as numpy array
    """
    # Apply voice parameters to the text
    inputs = self._prepare_tts_inputs(text, voice_profile, emotion)

    # Generate speech
    with torch.no_grad():
      speech = self._generate_speech(inputs, voice_profile)

    # Apply post-processing effects
    audio_data = self._apply_post_processing(speech, voice_profile)

    # Save to file if output path is specified
    if output_path:
      sf.write(
        output_path,
        audio_data,
        self.config.get("audio", {}).get("sample_rate", 22050)
      )

    return audio_data

  def _prepare_tts_inputs(self, text: str, voice_profile: Dict[str, Any], emotion: Optional[str] = None) -> Dict[str, torch.Tensor]:
    """
    Prepare inputs for the TTS model.

    Args:
        text: Text to synthesize
        voice_profile: Voice profile parameters
        emotion: Emotional tone (optional)

    Returns:
        Dictionary of model inputs
    """
    processor = self.processors["tts"]

    # Process text input
    inputs = processor(text=text, return_tensors="pt").to(self.device)

    # Get speaker embedding
    embedding = None

    # First try speaker_id from voice profile
    speaker_id = voice_profile.get("speaker_id")
    if speaker_id and speaker_id in self.speaker_embeddings:
      embedding = self.speaker_embeddings[speaker_id]

    # Next try explicit speaker_embedding
    if embedding is None and "speaker_embedding" in voice_profile:
      speaker_embedding = voice_profile["speaker_embedding"]
      if isinstance(speaker_embedding, str) and speaker_embedding in self.speaker_embeddings:
        embedding = self.speaker_embeddings[speaker_embedding]
      elif isinstance(speaker_embedding, str) and os.path.exists(speaker_embedding):
        embedding = torch.load(speaker_embedding, map_location=self.device)
      elif hasattr(speaker_embedding, "to"):  # If it's a tensor
        embedding = speaker_embedding.to(self.device)

    # If still no embedding, try gender-based fallbacks
    if embedding is None:
      gender = voice_profile.get("gender", "neutral")
      if f"{gender}_medium" in self.speaker_embeddings:
        embedding = self.speaker_embeddings[f"{gender}_medium"]
      elif gender in self.speaker_embeddings:
        embedding = self.speaker_embeddings[gender]

    # Final fallback to any available embedding
    if embedding is None and self.speaker_embeddings:
      if "default" in self.speaker_embeddings:
        embedding = self.speaker_embeddings["default"]
      else:
        # Just use the first available embedding
        embedding = next(iter(self.speaker_embeddings.values()))

    # If we still don't have an embedding, raise a helpful error
    if embedding is None:
      raise ValueError(
        "No speaker embeddings available. Please run: "
        "python -m voice_generator.download_models --embeddings-only"
      )

    # Add the embedding to inputs
    inputs["speaker_embeddings"] = embedding.unsqueeze(0) if embedding.dim() == 1 else embedding

    # Add emotion if available and model supports it
    if emotion and hasattr(processor, "process_emotion"):
      emotion_inputs = processor.process_emotion(emotion, return_tensors="pt").to(self.device)
      inputs.update(emotion_inputs)

    return inputs

  def _generate_speech(self, inputs: Dict[str, torch.Tensor], voice_profile: Dict[str, Any]) -> torch.Tensor:
    """
    Generate speech using the TTS model.

    Args:
        inputs: Processed inputs for the model
        voice_profile: Voice profile parameters

    Returns:
        Generated speech tensor
    """
    model = self.models["tts"]
    vocoder = self.vocoders["default"]

    # Extract voice modification parameters
    speed = voice_profile.get("speed", 1.0)
    pitch = voice_profile.get("pitch", 0)

    # Generate speech (model-specific handling)
    if "speecht5" in str(type(model)):
      # SpeechT5 specific generation
      speech = model.generate_speech(
        inputs["input_ids"].squeeze(),
        inputs.get("speaker_embeddings", None),
        vocoder=vocoder
      )
    else:
      # Generic generation for other models
      output = model.generate(**inputs)
      speech = output.waveform.squeeze()

    return speech

  def _apply_post_processing(self, speech: torch.Tensor, voice_profile: Dict[str, Any]) -> np.ndarray:
    """
    Apply post-processing effects to the generated speech.

    Args:
        speech: Generated speech tensor
        voice_profile: Voice profile parameters

    Returns:
        Processed audio as numpy array
    """
    # Convert to numpy array
    audio_data = speech.cpu().numpy()

    # Get effect parameters from voice profile
    effects = voice_profile.get("effects", {})

    # Skip if no effects
    if not effects:
      return audio_data

    # Apply effect chain
    return apply_effect_chain(audio_data, effects,
                              sample_rate=self.config.get("audio", {}).get("sample_rate", 22050))


def initialize_voice_models(config: Dict[str, Any], use_gpu: bool = True) -> VoiceGenerator:
  """
  Initialize the voice generation models.

  Args:
      config: Configuration dictionary
      use_gpu: Whether to use GPU for inference

  Returns:
      Initialized VoiceGenerator instance
  """
  voice_config = config.get("voice_generator", {})
  return VoiceGenerator(voice_config, use_gpu)


def generate_voices(script_data: Dict[str, Any], config: Optional[Dict[str, Any]] = None) -> Dict[str, Dict[str, Any]]:
  """
  Generate voices for all characters in a script.

  Args:
      script_data: Parsed script data
      config: Configuration dictionary (optional)

  Returns:
      Dictionary mapping character codes to voice profiles and audio files
  """
  if config is None:
    # Import here to avoid circular imports
    from utils.config_loader import load_config
    config = load_config()

  # Get voice generator configuration
  voice_config = config.get("voice_generator", {})

  # Determine output directory
  output_dir = os.path.join(
    config.get("general", {}).get("directories", {}).get("output", "outputs"),
    "voices"
  )

  # Initialize voice generator
  use_gpu = config.get("general", {}).get("processing", {}).get("use_gpu", True)
  generator = initialize_voice_models(config, use_gpu)

  # Generate voices
  logger.info(f"Generating voices for {len(script_data.get('characters', {}))} characters")
  character_voices = generator.generate_character_voices(script_data, output_dir)

  logger.info(f"Generated {len(character_voices)} character voices")
  return character_voices


def generate_voice_clip(text: str, voice_profile: Dict[str, Any],
                        emotion: Optional[str] = None,
                        output_path: Optional[str] = None,
                        config: Optional[Dict[str, Any]] = None) -> str:
  """
  Generate a single voice clip.

  Args:
      text: Text to synthesize
      voice_profile: Voice profile parameters
      emotion: Emotional tone (optional)
      output_path: Path to save the audio file (optional)
      config: Configuration dictionary (optional)

  Returns:
      Path to the generated audio file
  """
  if config is None:
    # Import here to avoid circular imports
    from utils.config_loader import load_config
    config = load_config()

  # Create temporary file if output_path is not specified
  if output_path is None:
    fd, output_path = tempfile.mkstemp(suffix=".wav")
    os.close(fd)

  # Initialize voice generator
  use_gpu = config.get("general", {}).get("processing", {}).get("use_gpu", True)
  generator = initialize_voice_models(config, use_gpu)

  # Generate speech
  generator.generate_voice_clip(text, voice_profile, emotion, output_path)

  return output_path


def apply_voice_effect(audio_path: str, effect_type: str, parameters: Dict[str, Any],
                       output_path: Optional[str] = None) -> str:
  """
  Apply an effect to a voice clip.

  Args:
      audio_path: Path to the input audio file
      effect_type: Type of effect to apply (reverb, echo, etc.)
      parameters: Effect-specific parameters
      output_path: Path to save the processed audio file (optional)

  Returns:
      Path to the processed audio file
  """
  try:
    # Create output path if not specified
    if output_path is None:
      output_path = f"{os.path.splitext(audio_path)[0]}_{effect_type}.wav"

    # Load audio
    audio_data, sample_rate = sf.read(audio_path)

    # Apply effect
    effects = {effect_type: parameters}
    processed_audio = apply_effect_chain(audio_data, effects, sample_rate)

    # Save processed audio
    sf.write(output_path, processed_audio, sample_rate)

    return output_path

  except Exception as e:
    logger.error(f"Error applying voice effect {effect_type}: {str(e)}")
    return audio_path  # Return original file on error


def load_voice_profile(profile_path: str) -> Dict[str, Any]:
  """
  Load a voice profile from a file.

  Args:
      profile_path: Path to the voice profile JSON file

  Returns:
      Voice profile dictionary
  """
  try:
    with open(profile_path, 'r') as f:
      return json.load(f)
  except Exception as e:
    logger.error(f"Error loading voice profile: {str(e)}")
    return {}


def save_voice_profile(voice_profile: Dict[str, Any], profile_path: str) -> bool:
  """
  Save a voice profile to a file.

  Args:
      voice_profile: Voice profile dictionary
      profile_path: Path to save the voice profile

  Returns:
      True if successful, False otherwise
  """
  try:
    with open(profile_path, 'w') as f:
      json.dump(voice_profile, f, indent=2)
    return True
  except Exception as e:
    logger.error(f"Error saving voice profile: {str(e)}")
    return False