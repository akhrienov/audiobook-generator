# Sound Library

This directory contains the sound effect library for the audio drama generator.

## Structure

The sound library is organized into categories:

```
sound_library/
├── ambient/        # Background ambient sounds
│   ├── nature/     # Nature sounds (rain, wind, forest, etc.)
│   ├── urban/      # Urban sounds (traffic, crowd, etc.)
│   └── interior/   # Interior sounds (room tone, etc.)
├── sfx/            # Sound effects
│   ├── doors/      # Door sounds (opening, closing, knocking)
│   ├── footsteps/  # Footstep sounds on various surfaces
│   ├── impacts/    # Impact and collision sounds
│   ├── technology/ # Technology sounds (beeps, machines, etc.)
│   └── vehicles/   # Vehicle sounds (car, train, boat, etc.)
├── transitions/    # Scene transition sounds
│   ├── dramatic/   # Dramatic transitions
│   ├── flashback/  # Flashback transitions
│   └── time/       # Time passing transitions
└── weather/        # Weather sounds
    ├── rain/       # Rain sounds (light, heavy, etc.)
    ├── thunder/    # Thunder sounds
    ├── wind/       # Wind sounds (light breeze, howling, etc.)
    └── misc/       # Other weather sounds
```

## File Naming

Files should be named descriptively with consistent formatting:

```
[category]_[description]_[variant].wav
```

Examples:
- `ambient_rain_light.wav`
- `sfx_door_creak.wav`
- `transition_flashback_echo.wav`

## File Format

All sound files should be:
- WAV format
- 44.1kHz or 48kHz sample rate
- 16-bit or 24-bit depth
- Mono or stereo as appropriate

## Metadata

Each sound file should have a corresponding metadata file with the same name but `.json` extension:

```json
{
  "name": "Light Rain",
  "description": "Light rainfall on a surface",
  "duration": 30.5,
  "loop_compatible": true,
  "tags": ["rain", "light", "ambient", "weather", "gentle", "background"],
  "intensity": 2,
  "source": "recorded_studio"
}
```

## Adding New Sounds

1. Place the sound file in the appropriate category directory
2. Create a corresponding metadata file
3. Update the sound index with `python -m sound_manager.update_index`