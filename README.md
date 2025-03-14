# Automated Audio Drama Generator

A Python application that transforms structured markdown audio drama scripts into fully-produced audio dramas with multiple character voices, sound effects, and music.

## Features

- Parse markdown-formatted audio drama scripts
- Generate distinct character voices based on script descriptions
- Add appropriate sound effects and ambient sounds
- Mix all audio elements with proper timing and transitions
- Produce high-quality, production-ready audio files

## Requirements

- Python 3.9+
- CUDA-compatible GPU (recommended)
- 16GB+ RAM recommended

## Installation

1. Clone this repository:
```bash
  git clone https://github.com/yourusername/audio-drama-generator.git
  cd audio-drama-generator
```

2. Create a virtual environment:
```bash
  python -m venv venv
  source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
  pip install -r requirements.txt
```

4. Download required models:
```bash
  python -m models.download_models
```

## Usage

1. Prepare your markdown script following the template in `sample_scripts/`
2. Run the generator:
```bash
  python main.py --script path/to/your/script.md --output output.wav
```

3. Find your audio drama in the specified output location

## Project Structure

- `script_parser/`: Script parsing and structure extraction
- `voice_generator/`: TTS and voice processing
- `sound_manager/`: Sound effect selection and processing
- `audio_mixer/`: Audio track mixing and production
- `production_engine/`: Main production coordination
- `models/`: Model management
- `ui/`: User interface
- `utils/`: Utility functions
- `tests/`: Unit and integration tests

## Testing

Run tests with:
```bash
  pytest
```

## License

[MIT License](LICENSE)