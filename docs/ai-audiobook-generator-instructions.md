# Automated Audio Drama Generator: Development Instructions

## Project Overview

This document provides comprehensive instructions for developing a fully automated system that transforms structured audio drama scripts into production-ready audio files. The system will parse script files containing character dialogue, narration, and production notes, then generate voices, sound effects, and music to produce a complete audio drama without manual intervention.

## Core Requirements

1. Parse structured markdown scripts containing dialogue, character descriptions, and production notes
2. Generate distinct character voices based on script descriptions using local AI models
3. Add appropriate sound effects and ambient sounds as specified in the script
4. Mix all audio elements together with proper timing and transitions
5. Produce a final, production-ready audio file
6. Deploy as a standalone application that can run locally and on RunPods

## System Architecture

The system will consist of the following components:

1. **Script Parser**: Analyzes the markdown script to extract characters, dialogue, and production notes
2. **Voice Generator**: Creates distinct voices for each character using local Hugging Face models
3. **Sound Effect Manager**: Selects and applies appropriate sound effects
4. **Audio Mixer**: Combines all elements with proper timing
5. **Production Engine**: Coordinates the entire process from input to output

## Detailed Implementation Guide

### 1. Script Parser Module

#### Key Functions:

```python
def parse_script(script_path):
    """
    Parse a markdown script file into a structured format.
    
    Args:
        script_path (str): Path to the markdown script file
        
    Returns:
        dict: Structured script data with sections for characters, scenes, dialogue, and production notes
    """
    
def extract_characters(script_data):
    """
    Extract character descriptions from script data.
    
    Args:
        script_data (str): Raw script content
        
    Returns:
        dict: Characters with their voice descriptions and attributes
    """
    
def extract_dialogue_sequences(script_data):
    """
    Extract dialogue sequences with speaker identification and timing.
    
    Args:
        script_data (str): Raw script content
        
    Returns:
        list: Sequence of dialogue elements with speaker, text, and timing information
    """
    
def extract_sound_cues(script_data):
    """
    Extract sound effect cues from script data.
    
    Args:
        script_data (str): Raw script content
        
    Returns:
        list: Sound cues with type, description, and timing information
    """
```

#### Implementation Notes:

- Use regex patterns to identify character sections, dialogue, and sound cues
- Create a structured JSON representation of the script for processing
- Implement special handling for nested elements like flashbacks
- Store timing relationships between dialogue and sound effects

### 2. Voice Generation Module

#### Key Functions:

```python
def initialize_voice_models():
    """
    Initialize the voice generation models from Hugging Face.
    
    Returns:
        dict: Loaded voice models ready for generation
    """
    
def generate_character_voice_profile(character_description):
    """
    Generate a voice profile based on character description.
    
    Args:
        character_description (str): Textual description of the character's voice
        
    Returns:
        dict: Voice parameters for this character
    """
    
def generate_voice_clip(text, voice_profile, emotion=None):
    """
    Generate a voice clip for the given text using the specified voice profile.
    
    Args:
        text (str): The text to convert to speech
        voice_profile (dict): Voice parameters to use
        emotion (str, optional): Emotional tone for the delivery
        
    Returns:
        bytes: Audio data for the generated speech
    """
    
def apply_voice_effects(audio_data, effect_type, parameters):
    """
    Apply post-processing effects to a voice clip.
    
    Args:
        audio_data (bytes): The raw audio data
        effect_type (str): Type of effect to apply (reverb, echo, etc.)
        parameters (dict): Effect-specific parameters
        
    Returns:
        bytes: Processed audio data
    """
```

#### Implementation Notes:

- Use Coqui TTS (locally deployed) for base voice generation
- Use Hugging Face's SpeechT5 or similar models for voice characteristics
- Implement voice modification based on character descriptions
- Use RVC (Retrieval-based Voice Conversion) models for voice characteristics
- Apply effects for special audio treatments (reverb, echo, etc.)

### 3. Sound Effect Manager

#### Key Functions:

```python
def initialize_sound_library(library_path):
    """
    Initialize the sound effect library.
    
    Args:
        library_path (str): Path to the sound effect library
        
    Returns:
        dict: Categorized sound effects ready for use
    """
    
def select_sound_effect(description, category=None):
    """
    Select an appropriate sound effect based on description.
    
    Args:
        description (str): Textual description of the needed sound
        category (str, optional): Category to search within
        
    Returns:
        str: Path to the selected sound effect file
    """
    
def generate_ambient_sound(description, duration):
    """
    Generate ambient sound based on description.
    
    Args:
        description (str): Textual description of the ambient sound
        duration (float): Duration in seconds
        
    Returns:
        bytes: Audio data for the generated ambient sound
    """
    
def modify_sound_effect(sound_data, modifications):
    """
    Apply modifications to a sound effect.
    
    Args:
        sound_data (bytes): The raw sound data
        modifications (dict): Modifications to apply (volume, pitch, etc.)
        
    Returns:
        bytes: Modified sound data
    """
```

#### Implementation Notes:

- Use a categorized local sound effect library
- Implement text similarity matching to find appropriate sounds
- Use AudioCraft or similar for generating missing effects
- Apply sound modifications based on script directions (increasing wind, etc.)

### 4. Audio Mixer Module

#### Key Functions:

```python
def create_empty_session(duration, sample_rate=44100):
    """
    Create an empty audio mixing session.
    
    Args:
        duration (float): Duration in seconds
        sample_rate (int): Sample rate for the session
        
    Returns:
        MixingSession: New mixing session object
    """
    
def add_track(session, track_type, name):
    """
    Add a new track to the mixing session.
    
    Args:
        session (MixingSession): The mixing session
        track_type (str): Type of track (voice, sound, music)
        name (str): Name for the track
        
    Returns:
        int: Track ID
    """
    
def place_audio_element(session, track_id, audio_data, start_time, volume=1.0):
    """
    Place an audio element on a track.
    
    Args:
        session (MixingSession): The mixing session
        track_id (int): Track to place the element on
        audio_data (bytes): Audio data to place
        start_time (float): Start time in seconds
        volume (float): Volume multiplier
        
    Returns:
        int: Element ID
    """
    
def apply_track_effect(session, track_id, effect_type, parameters):
    """
    Apply an effect to an entire track.
    
    Args:
        session (MixingSession): The mixing session
        track_id (int): Track to apply the effect to
        effect_type (str): Type of effect to apply
        parameters (dict): Effect parameters
    """
    
def render_final_mix(session, output_path, format="wav"):
    """
    Render the final mix to a file.
    
    Args:
        session (MixingSession): The mixing session
        output_path (str): Path to write the output file
        format (str): Output format
        
    Returns:
        str: Path to the rendered file
    """
```

#### Implementation Notes:

- Use pydub or similar for audio manipulation
- Implement cross-fading between elements
- Control volume dynamics based on script notes
- Apply appropriate compression and EQ to the final mix

### 5. Production Engine

#### Key Functions:

```python
def generate_production(script_path, output_path, config=None):
    """
    Generate a complete audio production from a script.
    
    Args:
        script_path (str): Path to the script file
        output_path (str): Path for the output file
        config (dict, optional): Configuration options
        
    Returns:
        str: Path to the final production file
    """
    
def process_scene(script_scene, session, character_voices):
    """
    Process a single scene from the script.
    
    Args:
        script_scene (dict): Scene data from the script
        session (MixingSession): Mixing session to add to
        character_voices (dict): Character voice profiles
        
    Returns:
        float: End time of the scene
    """
    
def process_dialogue_sequence(dialogue_sequence, session, character_voices, start_time):
    """
    Process a dialogue sequence.
    
    Args:
        dialogue_sequence (list): Sequence of dialogue elements
        session (MixingSession): Mixing session to add to
        character_voices (dict): Character voice profiles
        start_time (float): Start time for the sequence
        
    Returns:
        float: End time of the sequence
    """
    
def handle_special_production_notes(note, session, current_time):
    """
    Handle special production notes.
    
    Args:
        note (dict): Production note data
        session (MixingSession): Mixing session to modify
        current_time (float): Current position in the timeline
        
    Returns:
        dict: Any changes to make to the production state
    """
```

#### Implementation Notes:

- Coordinate all components in the right sequence
- Implement error handling and recovery strategies
- Use a state machine approach to track production progress
- Generate detailed logs of the production process

## Model Selection and Configuration

### Voice Generation Models

For local voice generation without external APIs, use these Hugging Face models:

1. **Base TTS Model**: microsoft/speecht5_tts or ggerganov/whisper.cpp
2. **Voice Conversion**: RVC (Retrieval-based Voice Conversion) models
3. **Voice Style Transfer**: StyleTTS2 for voice characteristics

### Sound Generation Models

1. **Audio Generation**: facebook/audiogen-medium for ambient sounds
2. **Sound Effect Classification**: MIT/ast-fsd50k for matching sound descriptions

## Implementation Workflow

1. Create a script parser that extracts structured data from your markdown files
2. Implement voice generation using local models
3. Build sound effect selection and generation components
4. Develop audio mixing capabilities
5. Create the production orchestration engine
6. Add a simple UI for configuration and monitoring
7. Package the application for local deployment
8. Configure for RunPods deployment

## Testing and Validation

1. Test with simple dialogue-only scripts first
2. Add complexity with sound effects
3. Test with flashback sequences and special effects
4. Validate with multi-character scenes
5. Test full production workflow end-to-end

## RunPods Deployment Configuration

```yaml
name: audio-drama-generator
image: your-docker-registry/audio-drama-generator:latest
resources:
  gpu: 1
  cpu: 4
  memory: 16Gi
storage:
  - mountPath: /data
    size: 20Gi
ports:
  - port: 8080
    targetPort: 8080
    protocol: TCP
    name: http
env:
  - name: MODEL_PATH
    value: /models
  - name: SOUND_LIBRARY_PATH
    value: /data/sounds
  - name: OUTPUT_PATH
    value: /data/output
```

## Optimization Considerations

1. Use half-precision (FP16) for model inference to improve performance
2. Cache generated voice clips for reuse across similar lines
3. Process scenes in parallel where possible
4. Pre-render common sound effects
5. Use GPU acceleration for voice and sound generation

## Future Enhancements

1. Implement AI-driven timing for more natural pauses
2. Add adaptive music composition based on scene emotion
3. Develop voice profile fine-tuning for specific characters
4. Create automated quality checks for the final production

This comprehensive guide provides all the necessary components to build a fully automated audio drama production system using local AI models. By following these instructions, you can develop an application that transforms your structured scripts into complete audio productions without manual intervention.
