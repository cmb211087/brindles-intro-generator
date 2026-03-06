# The Brindles - Automated Intro/Outro Generator

Automatically generates branded intro and outro videos for The Brindles YouTube channel.

- **Intro** (~16 sec): Detects the most exciting moments from your raw footage and assembles them into a highlight reel with your logo and signature music.
- **Outro** (~18 sec): Static branded end card with logo, subscribe text, and space for YouTube end screen elements.

## Quick Start

### 1. One-Time Setup

**Mac:**
```bash
chmod +x setup.sh
./setup.sh
```

**Windows:**
Double-click `setup.bat`

### 2. Add Your Assets

Place these files in the `assets/` folder:

| File | Description |
|------|-------------|
| `logo.png` | Your Brindles circular logo (any size, will be auto-scaled) |
| `intro_music.mp3` | Signature intro music track |
| `outro_music.mp3` | Signature outro music track |

The font (Montserrat Bold) is downloaded automatically during setup.

### 3. Generate Videos

1. Copy raw clips from your DJI Osmo Pocket 3 into `input/`
2. **Mac:** Double-click `generate.sh` / **Windows:** Double-click `generate.bat`
3. Wait ~2-5 minutes
4. Pick up `output/intro.mp4` and `output/outro.mp4`
5. Open CapCut, drag intro to the start, edit your content, drag outro to the end
6. Export and upload!

## Finding Free Music

Search for upbeat, family-friendly tracks on these royalty-free music sites:

- **[Pixabay Music](https://pixabay.com/music/)** - Search "upbeat fun family". Free, no attribution required.
- **[Incompetech](https://incompetech.com/music/)** - Kevin MacLeod's library. Free with attribution (credit in video description).
- **[YouTube Audio Library](https://studio.youtube.com/channel/UC/music)** - Available in YouTube Studio. Filter by mood and genre.

Download your chosen tracks and save as:
- `assets/intro_music.mp3` - Something upbeat and energetic (~20-30 seconds is enough)
- `assets/outro_music.mp3` - Something warm and chill (~20-30 seconds is enough)

## How It Works

### Intro Generation
1. Scans all video files in `input/`
2. Splits each clip into scenes using PySceneDetect
3. Scores each scene for audio excitement (loudness, sudden changes) using Librosa
4. Scores each scene for visual action (camera/subject motion) using OpenCV optical flow
5. Selects the top 5 most exciting moments
6. Assembles: title card + 5 highlight clips + logo reveal
7. Overlays your signature intro music

### Outro Generation
Generated once on first run, then reused for every video. Creates a branded end card with your logo and subscribe text, with the lower portion kept clear for YouTube end screen cards.

## Project Structure

```
brindles-intro-generator/
├── generate.py          # Main entry point
├── src/
│   ├── config.py        # Brand constants and settings
│   ├── highlight_detector.py  # Scene detection + scoring engine
│   ├── intro_builder.py       # Intro video composer
│   └── outro_builder.py       # Outro video composer
├── assets/
│   ├── logo.png         # Your logo (you provide)
│   ├── intro_music.mp3  # Intro track (you provide)
│   ├── outro_music.mp3  # Outro track (you provide)
│   └── fonts/
│       └── Montserrat-Bold.ttf  # Auto-downloaded
├── input/               # Drop raw clips here
└── output/              # Generated videos appear here
```

## Requirements

- Python 3.10+
- FFmpeg
- ~2GB disk space for dependencies

## Troubleshooting

**"No video files found"** - Make sure your clips are in the `input/` folder with .mp4 or .mov extensions.

**"Missing required assets"** - You need to provide `intro_music.mp3`, `outro_music.mp3`, and the font. Run setup again.

**Intro looks wrong** - Try with different clips. The highlight detector works best with varied footage (different scenes, activity levels).

**Very slow** - First run installs dependencies. Subsequent runs should take 2-5 minutes depending on how many clips you have.
