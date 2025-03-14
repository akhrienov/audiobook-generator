# Sample Scripts

This directory contains sample markdown-formatted scripts for the audio drama generator.

## Script Format

Scripts should follow this format:

```markdown
# TITLE OF DRAMA

## PREMISE
A brief description of the drama.

## SPEAKER NOTES

**CHARACTERS:**

**Character Name** - Character description including voice characteristics.

**Another Character** - Character description including voice characteristics.

**Special Audio Considerations:**
- Any special audio notes or requirements

## SCENE_NAME

[sound: description]

**Character:** Dialogue text.

**Another Character:** (emotion) Dialogue text.

[sound: another sound description]

**Narrator:** Narration text.

## ANOTHER_SCENE

...
```

## Required Elements

1. **Title**: The title of the audio drama
2. **Premise**: A brief description of the drama
3. **Speaker Notes**: Contains character descriptions and special audio considerations
4. **Scenes**: Sections with scene names, containing dialogue and sound cues

## Dialogue Format

- Character dialogue is formatted as `**Character Name:** Dialogue text.`
- Emotions or delivery notes can be included in parentheses: `**Character:** (angry) Dialogue text.`
- Internal thoughts or special voice treatments can be formatted with asterisks: `**Character:** *Internal thought text*`

## Sound Cues

Sound cues are formatted as: `[sound: description]`

Examples:
- `[sound: door creaking open]`
- `[sound: heavy rain intensifying]`
- `[sound: flashback transition]`

## Scene Transitions

Scenes are separated by Markdown headers (`## SCENE_NAME`).

## Special Effects

Special audio effects should be noted in the Speaker Notes section and may be referenced in the script with specific sound cues.

## Example

See `lighthouse.md` for a complete example script.