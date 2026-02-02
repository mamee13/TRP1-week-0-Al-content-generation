# 📋 Style Presets: Mapping Imagination to Parameters

The framework uses a centralized preset system to translate high-level style keywords into complex, vendor-optimized prompts.

## 🎵 Music Presets (`src/ai_content/presets/music.py`)

Presets for music generation include not just prompts, but also technical metadata like **BPM** and **Mood**.

| Preset | Prompt Snippet | BPM | Mood |
|--------|----------------|-----|------|
| `jazz` | [Smooth Jazz Fusion] [Walking Bass, Brushed Drums] | 95 | Nostalgic |
| `blues` | [Delta Blues] [Bluesy Guitar Arpeggio] | 72 | Soulful |
| `ethio-jazz` | [Ethio-Jazz Influence] [Masenqo-inspired Strings] | 85 | Mystical |
| `cinematic` | [Epic Orchestral] [Sweeping Strings, Powerful Brass] | 100 | Epic |
| `electronic` | [Progressive House] [Driving Bass, Synth Arpeggios] | 128 | Euphoric |
| `ambient` | [Ambient Soundscape] [Ethereal Pads, Modular Synth] | 60 | Peaceful |
| `lofi` | [Lo-fi Hip-hop] [Chill Beats, Nostalgic Piano] | 85 | Relaxed |

## 🎬 Video Presets (`src/ai_content/presets/video.py`)

Video presets are optimized for cinematic motion and visual storytelling, specifying **Aspect Ratio** and **Duration**.

| Preset | Description | Aspect | Keywords |
|--------|-------------|--------|----------|
| `nature` | Majestic lion in savanna, golden hour. | 16:9 | Documentary, Wildlife |
| `urban` | Neon-lit Tokyo rain, cyberpunk aesthetic. | 21:9 | Cyberpunk, Urban |
| `space` | Astronaut in space station, Earth view. | 16:9 | Sci-fi, Space |
| `abstract` | Flowing liquid metal, geometric shapes. | 1:1 | Artistic, Commercial |
| `ocean` | Turquoise waves, sunbeams filtering water. | 16:9 | Scenic, Underwater |
| `fantasy` | Ancient dragon soaring misty mountain peaks. | 21:9 | High Fantasy, Epic |

## 🚀 How Presets Work

1. **Translation**: The `get_preset(name)` function retrieves the `dataclass` containing the prompt and parameters.
2. **Optimization**: Providers can further wrap these prompts with vendor-specific tags (e.g., Google Lyria's bracketed tags like `[Solo Piano]`).
3. **Extensibility**: New presets can be added by simply appending to the `MUSIC_PRESETS` or `VIDEO_PRESETS` lists in the respective modules.

### Custom Preset Example: `tenx-special`
We added `tenx-special` to demonstrate the flexibility of the registry:
- **Style**: Futuristic, AI-agentic, techno-optimist.
- **Prompt**: Focuses on "silicon pulses" and "digital frontiers" to align with the challenge theme.
