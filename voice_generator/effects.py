#!/usr/bin/env python3
"""
Voice effects module for the Automated Audio Drama Generator.

This module handles the application of audio effects to voice clips.
"""

import os
import logging
import tempfile
import numpy as np
from typing import Dict, List, Any, Optional, Tuple, Union

# Set up logging
logging.basicConfig(
  level=logging.INFO,
  format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

try:
  import librosa
  import librosa.effects
  from scipy import signal
  import soundfile as sf
  # Try to import pedalboard for advanced effects if available
  try:
    from pedalboard import Pedalboard, Reverb, Compressor, Gain, LadderFilter, Phaser
    from pedalboard import Distortion, Delay, PitchShift, Chorus
    PEDALBOARD_AVAILABLE = True
  except ImportError:
    logger.warning("Pedalboard library not available, falling back to basic effects")
    PEDALBOARD_AVAILABLE = False

except ImportError as e:
  logger.error(f"Error importing audio processing libraries: {e}")
  raise


def apply_reverb(audio: np.ndarray, room_size: float = 0.5, damping: float = 0.5,
                 wet_level: float = 0.33, dry_level: float = 0.4,
                 sample_rate: int = 22050) -> np.ndarray:
  """
  Apply reverb effect to audio.

  Args:
      audio: Input audio data as numpy array
      room_size: Size of the simulated room (0.0-1.0)
      damping: Damping factor (0.0-1.0)
      wet_level: Level of processed signal (0.0-1.0)
      dry_level: Level of original signal (0.0-1.0)
      sample_rate: Audio sample rate

  Returns:
      Processed audio data
  """
  if PEDALBOARD_AVAILABLE:
    # Use Pedalboard's high-quality reverb
    board = Pedalboard([
      Reverb(
        room_size=room_size,
        damping=damping,
        wet_level=wet_level,
        dry_level=dry_level
      )
    ])

    # Process audio
    processed_audio = board.process(audio.astype(np.float32), sample_rate)
    return processed_audio
  else:
    # Simple convolution reverb using scipy
    # Generate a simple impulse response
    duration = room_size * 3  # Longer room size = longer reverb tail
    impulse_response = np.exp(-np.linspace(0, duration, int(duration * sample_rate)))
    impulse_response = impulse_response * np.random.randn(len(impulse_response))
    impulse_response = impulse_response / np.abs(impulse_response).max()

    # Apply damping (reduce high frequencies in the reverb tail)
    if damping > 0:
      b, a = signal.butter(2, damping, btype='low')
      impulse_response = signal.filtfilt(b, a, impulse_response)

    # Convolve the audio with the impulse response
    reverb_signal = signal.convolve(audio, impulse_response, mode='full')[:len(audio)]

    # Mix dry and wet signals
    return (dry_level * audio) + (wet_level * reverb_signal)


def apply_echo(audio: np.ndarray, delay: float = 0.3, decay: float = 0.5, sample_rate: int = 22050) -> np.ndarray:
  """
  Apply echo effect to audio.

  Args:
      audio: Input audio data as numpy array
      delay: Delay time in seconds
      decay: Decay factor for each echo (0.0-1.0)
      sample_rate: Audio sample rate

  Returns:
      Processed audio data
  """
  if PEDALBOARD_AVAILABLE:
    # Use Pedalboard's delay effect
    board = Pedalboard([
      Delay(
        delay_seconds=delay,
        feedback=decay,
        mix=0.5
      )
    ])

    # Process audio
    processed_audio = board.process(audio.astype(np.float32), sample_rate)
    return processed_audio
  else:
    # Manual delay implementation
    delay_samples = int(delay * sample_rate)

    # Create delayed signal
    delayed = np.zeros_like(audio)
    delayed[delay_samples:] = audio[:-delay_samples] * decay

    # Mix original and delayed signal
    result = audio + delayed

    # Normalize to prevent clipping
    result = result / np.abs(result).max() * np.abs(audio).max()

    return result


def apply_pitch_shift(audio: np.ndarray, semitones: float = 0.0, sample_rate: int = 22050) -> np.ndarray:
  """
  Apply pitch shifting to audio.

  Args:
      audio: Input audio data as numpy array
      semitones: Number of semitones to shift (positive = higher, negative = lower)
      sample_rate: Audio sample rate

  Returns:
      Processed audio data
  """
  if abs(semitones) < 0.1:  # Skip if shift is negligible
    return audio

  if PEDALBOARD_AVAILABLE:
    # Use Pedalboard's pitch shift
    board = Pedalboard([
      PitchShift(semitones=semitones)
    ])

    # Process audio
    processed_audio = board.process(audio.astype(np.float32), sample_rate)
    return processed_audio
  else:
    # Use librosa's pitch shift
    return librosa.effects.pitch_shift(audio, sr=sample_rate, n_steps=semitones)


def apply_timestretch(audio: np.ndarray, rate: float = 1.0, sample_rate: int = 22050) -> np.ndarray:
  """
  Apply time stretching to audio (changing speed without changing pitch).

  Args:
      audio: Input audio data as numpy array
      rate: Stretch factor (>1 = faster, <1 = slower)
      sample_rate: Audio sample rate

  Returns:
      Processed audio data
  """
  if abs(rate - 1.0) < 0.01:  # Skip if change is negligible
    return audio

  # Use librosa for time stretching
  return librosa.effects.time_stretch(audio, rate=rate)


def apply_distortion(audio: np.ndarray, amount: float = 0.1, sample_rate: int = 22050) -> np.ndarray:
  """
  Apply distortion effect to audio.

  Args:
      audio: Input audio data as numpy array
      amount: Distortion amount (0.0-1.0)
      sample_rate: Audio sample rate

  Returns:
      Processed audio data
  """
  if amount < 0.01:  # Skip if amount is negligible
    return audio

  if PEDALBOARD_AVAILABLE:
    # Use Pedalboard's distortion
    board = Pedalboard([
      Distortion(drive_db=amount * 25)  # Scale amount to reasonable drive_db value
    ])

    # Process audio
    processed_audio = board.process(audio.astype(np.float32), sample_rate)
    return processed_audio
  else:
    # Simple waveshaping distortion
    # Normalize the audio
    audio_norm = audio / (np.max(np.abs(audio)) + 1e-10)

    # Apply distortion
    k = 2 * amount / (1 - amount) if amount < 1.0 else 20
    distorted = np.tanh(k * audio_norm) / np.tanh(k) if k > 0 else audio_norm

    return distorted


def apply_tremolo(audio: np.ndarray, depth: float = 0.5, rate: float = 5.0, sample_rate: int = 22050) -> np.ndarray:
  """
  Apply tremolo effect (amplitude modulation) to audio.

  Args:
      audio: Input audio data as numpy array
      depth: Depth of the tremolo effect (0.0-1.0)
      rate: Rate of the tremolo in Hz
      sample_rate: Audio sample rate

  Returns:
      Processed audio data
  """
  if depth < 0.01:  # Skip if depth is negligible
    return audio

  # Generate modulation signal (sine wave)
  t = np.arange(len(audio)) / sample_rate
  mod = 1.0 - depth * 0.5 * (1.0 + np.sin(2 * np.pi * rate * t))

  # Apply modulation
  return audio * mod


def apply_filter(audio: np.ndarray, filter_type: str = "lowpass", cutoff: float = 0.5,
                 q: float = 1.0, sample_rate: int = 22050) -> np.ndarray:
  """
  Apply a filter effect to audio.

  Args:
      audio: Input audio data as numpy array
      filter_type: Type of filter ("lowpass", "highpass", "bandpass")
      cutoff: Normalized cutoff frequency (0.0-1.0, will be scaled to Nyquist)
      q: Q factor (resonance, higher = more resonant)
      sample_rate: Audio sample rate

  Returns:
      Processed audio data
  """
  if PEDALBOARD_AVAILABLE:
    # Use Pedalboard's filter
    cutoff_hz = cutoff * sample_rate / 2  # Convert normalized cutoff to Hz

    if filter_type == "lowpass":
      mode = LadderFilter.Mode.LPF24
    elif filter_type == "highpass":
      mode = LadderFilter.Mode.HPF24
    elif filter_type == "bandpass":
      mode = LadderFilter.Mode.BPF24
    else:
      logger.warning(f"Unknown filter type: {filter_type}, defaulting to lowpass")
      mode = LadderFilter.Mode.LPF24

    board = Pedalboard([
      LadderFilter(
        mode=mode,
        cutoff_hz=cutoff_hz,
        resonance=q,
        drive=0.0  # No added distortion
      )
    ])

    # Process audio
    processed_audio = board.process(audio.astype(np.float32), sample_rate)
    return processed_audio
  else:
    # Use scipy's filter
    nyquist = sample_rate / 2
    cutoff_hz = cutoff * nyquist  # Convert normalized cutoff to Hz

    # Design the filter
    if filter_type == "lowpass":
      b, a = signal.butter(4, cutoff_hz / nyquist, btype='lowpass')
    elif filter_type == "highpass":
      b, a = signal.butter(4, cutoff_hz / nyquist, btype='highpass')
    elif filter_type == "bandpass":
      bandwidth = cutoff_hz / q  # Convert Q to bandwidth
      low = max(10, cutoff_hz - bandwidth/2) / nyquist
      high = min(nyquist - 10, cutoff_hz + bandwidth/2) / nyquist
      b, a = signal.butter(2, [low, high], btype='bandpass')
    else:
      logger.warning(f"Unknown filter type: {filter_type}, defaulting to lowpass")
      b, a = signal.butter(4, cutoff_hz / nyquist, btype='lowpass')

    # Apply the filter
    return signal.filtfilt(b, a, audio)


def apply_eq(audio: np.ndarray, low: float = 1.0, mid: float = 1.0, high: float = 1.0,
             sample_rate: int = 22050) -> np.ndarray:
  """
  Apply a 3-band equalizer effect to audio.

  Args:
      audio: Input audio data as numpy array
      low: Gain for low frequencies (0.0-2.0, 1.0 = no change)
      mid: Gain for mid frequencies (0.0-2.0, 1.0 = no change)
      high: Gain for high frequencies (0.0-2.0, 1.0 = no change)
      sample_rate: Audio sample rate

  Returns:
      Processed audio data
  """
  # Skip if no EQ needed
  if abs(low - 1.0) < 0.01 and abs(mid - 1.0) < 0.01 and abs(high - 1.0) < 0.01:
    return audio

  # Crossover frequencies (in Hz)
  low_mid_crossover = 300
  mid_high_crossover = 3000

  nyquist = sample_rate / 2

  # Extract low band
  if abs(low - 1.0) >= 0.01:
    b, a = signal.butter(4, low_mid_crossover / nyquist, btype='lowpass')
    low_band = signal.filtfilt(b, a, audio) * low
  else:
    low_band = np.zeros_like(audio)

  # Extract high band
  if abs(high - 1.0) >= 0.01:
    b, a = signal.butter(4, mid_high_crossover / nyquist, btype='highpass')
    high_band = signal.filtfilt(b, a, audio) * high
  else:
    high_band = np.zeros_like(audio)

  # Extract mid band
  if abs(mid - 1.0) >= 0.01:
    b1, a1 = signal.butter(4, low_mid_crossover / nyquist, btype='highpass')
    b2, a2 = signal.butter(4, mid_high_crossover / nyquist, btype='lowpass')
    mid_band_1 = signal.filtfilt(b1, a1, audio)
    mid_band = signal.filtfilt(b2, a2, mid_band_1) * mid
  else:
    mid_band = np.zeros_like(audio)

  # If all bands are zero, just return the original
  if low == 0 and mid == 0 and high == 0:
    return np.zeros_like(audio)

  # If no EQ was actually applied, return the original
  if low == 1.0 and mid == 1.0 and high == 1.0:
    return audio

  # Mix bands with original
  if low == 1.0 and mid == 1.0 and high == 1.0:
    return audio
  elif low == 0.0 and mid == 0.0 and high == 0.0:
    return np.zeros_like(audio)
  else:
    # Combine the bands
    result = low_band + mid_band + high_band

    # Normalize to prevent clipping
    max_val = np.max(np.abs(result))
    if max_val > 1.0:
      result = result / max_val

    return result


def apply_compressor(audio: np.ndarray, threshold: float = -20.0, ratio: float = 4.0,
                     attack: float = 0.005, release: float = 0.1,
                     sample_rate: int = 22050) -> np.ndarray:
  """
  Apply compression effect to audio.

  Args:
      audio: Input audio data as numpy array
      threshold: Threshold in dB
      ratio: Compression ratio
      attack: Attack time in seconds
      release: Release time in seconds
      sample_rate: Audio sample rate

  Returns:
      Processed audio data
  """
  if PEDALBOARD_AVAILABLE:
    # Use Pedalboard's compressor
    board = Pedalboard([
      Compressor(
        threshold_db=threshold,
        ratio=ratio,
        attack_ms=attack * 1000,  # Convert to ms
        release_ms=release * 1000  # Convert to ms
      )
    ])

    # Process audio
    processed_audio = board.process(audio.astype(np.float32), sample_rate)
    return processed_audio
  else:
    # Simple compressor implementation
    # Convert threshold from dB to linear
    threshold_linear = 10 ** (threshold / 20.0)

    # Calculate attack and release coefficients
    attack_coef = np.exp(-1.0 / (sample_rate * attack))
    release_coef = np.exp(-1.0 / (sample_rate * release))

    # Prepare output array
    output = np.zeros_like(audio)

    # Initialize envelope
    envelope = 0

    # Process each sample
    for i in range(len(audio)):
      # Calculate envelope
      input_abs = abs(audio[i])
      if input_abs > envelope:
        envelope = attack_coef * envelope + (1 - attack_coef) * input_abs
      else:
        envelope = release_coef * envelope + (1 - release_coef) * input_abs

      # Calculate gain reduction
      if envelope > threshold_linear:
        gain_reduction = threshold_linear + (envelope - threshold_linear) / ratio
        gain = gain_reduction / envelope
      else:
        gain = 1.0

      # Apply gain
      output[i] = audio[i] * gain

    return output


def apply_noise(audio: np.ndarray, amount: float = 0.01, sample_rate: int = 22050) -> np.ndarray:
  """
  Add noise to audio.

  Args:
      audio: Input audio data as numpy array
      amount: Amount of noise to add (0.0-1.0)
      sample_rate: Audio sample rate

  Returns:
      Processed audio data
  """
  if amount < 0.001:  # Skip if amount is negligible
    return audio

  # Generate noise
  noise = np.random.randn(len(audio)) * amount

  # Add noise to audio
  noisy_audio = audio + noise

  # Clip to prevent values outside [-1, 1]
  noisy_audio = np.clip(noisy_audio, -1.0, 1.0)

  return noisy_audio


def apply_effect_chain(audio: np.ndarray, effects: Dict[str, Dict[str, Any]], sample_rate: int = 22050) -> np.ndarray:
  """
  Apply a chain of effects to audio.

  Args:
      audio: Input audio data as numpy array
      effects: Dictionary of effects and their parameters
      sample_rate: Audio sample rate

  Returns:
      Processed audio data
  """
  if not effects:
    return audio

  processed = audio.copy()

  # Process each effect in the chain
  for effect_type, params in effects.items():
    logger.debug(f"Applying effect: {effect_type} with params: {params}")

    if effect_type == "reverb":
      processed = apply_reverb(
        processed,
        room_size=params.get("room_size", 0.5),
        damping=params.get("damping", 0.5),
        wet_level=params.get("wet_level", 0.33),
        dry_level=params.get("dry_level", 0.4),
        sample_rate=sample_rate
      )

    elif effect_type == "echo" or effect_type == "delay":
      processed = apply_echo(
        processed,
        delay=params.get("delay", 0.3),
        decay=params.get("decay", 0.5),
        sample_rate=sample_rate
      )

    elif effect_type == "pitch_shift":
      processed = apply_pitch_shift(
        processed,
        semitones=params.get("semitones", 0.0),
        sample_rate=sample_rate
      )

    elif effect_type == "timestretch":
      processed = apply_timestretch(
        processed,
        rate=params.get("rate", 1.0),
        sample_rate=sample_rate
      )

    elif effect_type == "distortion":
      processed = apply_distortion(
        processed,
        amount=params.get("amount", 0.1),
        sample_rate=sample_rate
      )

    elif effect_type == "tremolo":
      processed = apply_tremolo(
        processed,
        depth=params.get("depth", 0.5),
        rate=params.get("rate", 5.0),
        sample_rate=sample_rate
      )

    elif effect_type in ["lowpass", "highpass", "bandpass"]:
      processed = apply_filter(
        processed,
        filter_type=effect_type,
        cutoff=params.get("cutoff", 0.5),
        q=params.get("q", 1.0),
        sample_rate=sample_rate
      )

    elif effect_type == "eq":
      processed = apply_eq(
        processed,
        low=params.get("low", 1.0),
        mid=params.get("mid", 1.0),
        high=params.get("high", 1.0),
        sample_rate=sample_rate
      )

    elif effect_type == "compressor":
      processed = apply_compressor(
        processed,
        threshold=params.get("threshold", -20.0),
        ratio=params.get("ratio", 4.0),
        attack=params.get("attack", 0.005),
        release=params.get("release", 0.1),
        sample_rate=sample_rate
      )

    elif effect_type == "noise":
      processed = apply_noise(
        processed,
        amount=params.get("amount", 0.01),
        sample_rate=sample_rate
      )

    else:
      logger.warning(f"Unknown effect type: {effect_type}, skipping")

  return processed