# AI Prompt: Develop an Automated Audio Drama Production System

## Task Description

Create a complete Python application that transforms structured markdown audio drama scripts into fully-produced audio dramas with multiple character voices, sound effects, and music. The system must be fully automated, requiring only the input script to generate a production-ready audio file.

## Input Requirements

The system must accept markdown-formatted scripts structured like the example provided, which contains:
- Character descriptions with voice characteristics
- Dialogue attributed to specific characters
- Sound effect cues in [sound: description] format
- Narrator lines
- Production notes for timing and emotional moments
- Scene transitions

## Output Requirements

The system should produce:
- A high-quality audio file (48kHz, 16-bit WAV) containing the complete audio drama
- All character voices differentiated according to script descriptions
- Sound effects and ambient sounds as specified in the script
- Appropriate timing for all audio elements
- Proper handling of flashbacks, internal thoughts, and special audio treatments

## Technical Requirements

1. Use only local Hugging Face models for TTS and audio processing
2. Implement proper script parsing using Python
3. Generate distinct voices for each character based on script descriptions
4. Include a sound effect library and selection system
5. Implement audio mixing with proper timing
6. Package as a deployable application for both local testing and RunPods deployment
7. Process script elements in the correct sequence
8. Apply specified audio effects (reverb, echo, etc.)

## Implementation Constraints

1. No external API dependencies (ElevenLabs, etc.)
2. Must run efficiently on a single GPU
3. Must handle scripts of 30+ minutes runtime
4. Must be fully automated with no manual intervention needed

## Key Challenges to Address

1. Accurate parsing of the structured markdown script
2. Generation of distinct character voices matching descriptions (raspy, deep, etc.)
3. Selection and timing of appropriate sound effects
4. Proper handling of overlapping sounds and dialogue
5. Implementation of special audio treatments (flashbacks, internal thoughts)
6. Creating natural-sounding transitions between scenes

## Specific Technical Approaches

### For Voice Generation
Use a combination of:
- Base TTS models from Hugging Face (microsoft/speecht5_tts)
- Voice conversion (RVC models) for character differentiation
- Voice modification for special treatments (reverb for internal thoughts, etc.)

### For Sound Effects
Implement:
- A categorized sound library with text-matching selection
- Ambient sound generation for backgrounds (fire crackling, wind, etc.)
- Volume automation for increasing/decreasing sounds (wind growing stronger)

### For Audio Mixing
Develop:
- Multi-track mixing with proper timing
- Crossfading between elements
- Dynamic volume adjustment
- Final mastering for production quality

## Example Code Structure

The application should follow this modular structure:

```
automated_audio_drama/
├── script_parser/
│   ├── __init__.py
│   ├── markdown_parser.py
│   ├── character_extractor.py
│   └── sound_cue_extractor.py
├── voice_generator/
│   ├── __init__.py
│   ├── tts_engine.py
│   ├── voice_converter.py
│   └── voice_effects.py
├── sound_manager/
│   ├── __init__.py
│   ├── sound_library.py
│   ├── sound_selector.py
│   └── ambient_generator.py
├── audio_mixer/
│   ├── __init__.py
│   ├── mixing_session.py
│   ├── track_processor.py
│   └── master_renderer.py
├── production_engine/
│   ├── __init__.py
│   ├── production_coordinator.py
│   ├── scene_processor.py
│   └── dialogue_processor.py
├── models/
│   └── model_loader.py
├── ui/
│   ├── __init__.py
│   └── simple_interface.py
├── utils/
│   ├── __init__.py
│   ├── audio_processing.py
│   └── text_processing.py
├── main.py
├── requirements.txt
└── Dockerfile
```

## Development Process

1. First develop the script parser to create a structured representation
2. Implement basic TTS using Hugging Face models
3. Add voice conversion for character differentiation
4. Develop sound effect selection and generation
5. Build the audio mixing engine
6. Create the production coordinator
7. Add testing and validation
8. Package for deployment

## Testing Plan

Provide a testing plan that validates:
1. Script parsing accuracy
2. Voice generation quality
3. Sound effect selection appropriateness
4. Audio mixing quality
5. End-to-end production quality

## Technical Considerations

1. GPU memory usage optimization
2. Processing time optimization
3. Audio quality vs. processing speed tradeoffs
4. Error handling for script parsing issues
5. Validation steps for script elements

## Deployment Specifications

Include Docker configuration and RunPods deployment instructions.

## Expected Deliverables

1. Complete source code with documentation
2. Requirements file with all dependencies
3. Dockerfile for containerization
4. RunPods deployment configuration
5. Example output from the provided script
6. Documentation on extending the system

## Technical Stack

- Python 3.9+
- PyTorch for model inference
- Hugging Face Transformers/models
- Pydub for audio processing
- Librosa for audio analysis
- ONNX Runtime for optimized inference
- Docker for containerization

Deliver a complete, working system that meets all requirements and can generate production-ready audio dramas from structured markdown scripts with no manual intervention.
