"""Brand constants and configuration for The Brindles intro/outro generator."""

import os

# Base directory (project root)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Brand colors
BRAND_COLOR = (43, 94, 167)        # #2B5EA7 blue (RGB)
BRAND_COLOR_HEX = "#2B5EA7"

# Video settings
RESOLUTION = (1920, 1080)
FPS = 30

# Intro settings
INTRO_CLIP_COUNT = 5               # Number of highlight clips
INTRO_CLIP_DURATION = 2.5          # Seconds per highlight clip
INTRO_COMING_UP_DURATION = 1.0     # "Coming up..." text duration
INTRO_LOGO_DURATION = 2.5          # Logo reveal duration
INTRO_MUSIC_FADE_IN = 0.5
INTRO_MUSIC_FADE_OUT = 1.0

# Outro settings
OUTRO_DURATION = 18.0
OUTRO_MUSIC_FADE_OUT = 3.0

# Highlight detection
MIN_SCENE_DURATION = 1.5           # Minimum scene length in seconds
MAX_SCENE_DURATION = 30.0          # Maximum scene length in seconds
AUDIO_WEIGHT = 0.5                 # Weight for audio score in combined ranking
VISUAL_WEIGHT = 0.5                # Weight for visual score in combined ranking
DIVERSITY_WINDOW = 30.0            # No two highlights from same 30-second window

# Paths (relative to BASE_DIR)
LOGO_PATH = os.path.join(BASE_DIR, "assets", "logo.png")
INTRO_MUSIC_PATH = os.path.join(BASE_DIR, "assets", "intro_music.mp3")
OUTRO_MUSIC_PATH = os.path.join(BASE_DIR, "assets", "outro_music.mp3")
FONT_PATH = os.path.join(BASE_DIR, "assets", "fonts", "Montserrat-Bold.ttf")
INPUT_DIR = os.path.join(BASE_DIR, "input")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

# Supported video extensions
VIDEO_EXTENSIONS = {".mp4", ".mov", ".MP4", ".MOV", ".avi", ".mkv"}
