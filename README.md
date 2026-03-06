# The Brindles - Automated Intro/Outro Generator

Automatically generates branded intro and outro videos for The Brindles YouTube channel.

- **Intro** (~16 sec): Detects the most exciting moments from your raw footage and assembles them into a highlight reel with your logo and signature music.
- **Outro** (~18 sec): Static branded end card with logo, subscribe text, and space for YouTube end screen elements.

## Quick Start

### 1. One-Time Setup

**Mac:**
```bash
./setup.sh
```

**Windows:**
Double-click `setup.bat`

This installs Python dependencies into a virtual environment. Logo, music, font, and outro are already included in the repo.

### 2. Generate Videos

1. Copy raw clips from your DJI Osmo Pocket 3 into `input/`
2. **Mac:** `./generate.sh` / **Windows:** Double-click `generate.bat`
3. Wait ~2-5 minutes
4. Pick up `output/intro.mp4` (outro is already in `output/`)
5. Open CapCut, drag intro to the start, edit your content, drag outro to the end
6. Export and upload!

## Music Credits

Intro and outro music by Kevin MacLeod (incompetech.com), licensed under CC BY 4.0. Credit in video descriptions:
> Music by Kevin MacLeod (incompetech.com) - Licensed under CC BY 4.0

To swap tracks, replace `assets/intro_music.mp3` or `assets/outro_music.mp3`. Good sources for free music:
- **[Pixabay Music](https://pixabay.com/music/)** - No attribution required
- **[Incompetech](https://incompetech.com/music/)** - Attribution required

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
│   ├── logo.png         # Brindles circular logo
│   ├── intro_music.mp3  # Intro track (Kevin MacLeod)
│   ├── outro_music.mp3  # Outro track (Kevin MacLeod)
│   └── fonts/
│       └── Montserrat-Bold.ttf  # Included
├── input/               # Drop raw clips here
└── output/              # Generated videos appear here
```

## Requirements

- Python 3.10+
- FFmpeg
- ~2GB disk space for dependencies

## Troubleshooting

**"No video files found"** - Make sure your clips are in the `input/` folder with .mp4 or .mov extensions.

**"Missing required assets"** - Assets should be in the repo already. If missing, re-clone or run `./setup.sh` again.

**Intro looks wrong** - Try with different clips. The highlight detector works best with varied footage (different scenes, activity levels).

**Very slow** - First run installs dependencies. Subsequent runs should take 2-5 minutes depending on how many clips you have.
