"""The Brindles - Automated Intro/Outro Generator.

Main entry point. Drop raw clips into input/, run this script,
and pick up intro.mp4 and outro.mp4 from output/.
"""

import os
import sys
import shutil

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.config import (
    INPUT_DIR, OUTPUT_DIR, LOGO_PATH, INTRO_MUSIC_PATH,
    OUTRO_MUSIC_PATH, FONT_PATH, VIDEO_EXTENSIONS,
)
from src.highlight_detector import detect_highlights, discover_clips
from src.intro_builder import build_intro
from src.outro_builder import build_outro


def log(msg):
    print(msg)


def check_assets():
    """Verify required assets exist."""
    missing = []
    if not os.path.exists(FONT_PATH):
        missing.append(f"Font: {FONT_PATH}")
    if not os.path.exists(INTRO_MUSIC_PATH):
        missing.append(f"Intro music: {INTRO_MUSIC_PATH}")
    if not os.path.exists(OUTRO_MUSIC_PATH):
        missing.append(f"Outro music: {OUTRO_MUSIC_PATH}")

    if not os.path.exists(LOGO_PATH):
        log(f"  Note: Logo not found at {LOGO_PATH} - will use text fallback")

    if missing:
        log("\nMissing required assets:")
        for m in missing:
            log(f"  - {m}")
        log("\nPlease see README.md for setup instructions.")
        log("You need to provide music files and the Montserrat font.")
        return False
    return True


def check_input():
    """Check that input directory has video files."""
    os.makedirs(INPUT_DIR, exist_ok=True)
    clips = discover_clips()
    if not clips:
        log(f"\nNo video files found in {INPUT_DIR}/")
        log(f"Supported formats: {', '.join(sorted(VIDEO_EXTENSIONS))}")
        log("\nCopy your raw clips from the DJI Osmo Pocket 3 into the input/ folder and try again.")
        return False
    return True


def main():
    log("=" * 55)
    log("  The Brindles - Intro/Outro Generator")
    log("=" * 55)
    log("")

    # Check assets
    log("[1/4] Checking assets...")
    if not check_assets():
        sys.exit(1)
    log("  All assets found.")

    # Check input clips
    log("")
    clips = discover_clips()
    has_input = len(clips) > 0

    # Ensure output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    outro_path = os.path.join(OUTPUT_DIR, "outro.mp4")
    intro_path = os.path.join(OUTPUT_DIR, "intro.mp4")

    # Generate outro if it doesn't exist yet
    if not os.path.exists(outro_path):
        log("[2/4] Generating outro (one-time)...")
        build_outro(outro_path, progress_fn=log)
        log("")
    else:
        log("[2/4] Outro already exists, skipping generation.")
        log("")

    # Generate intro from input clips
    if has_input:
        log(f"[3/4] Scanning {len(clips)} video clip(s) in input/...")
        log("[4/4] Analyzing highlights (this may take a few minutes)...")
        log("")

        highlights = detect_highlights(progress_fn=log)
        log("")

        log("Building intro from top highlights...")
        build_intro(highlights, intro_path, progress_fn=log)
    else:
        if not os.path.exists(intro_path):
            log("[3/4] No input clips found - skipping intro generation.")
            log("[4/4] To generate an intro, add video clips to input/ and run again.")
        else:
            log("[3/4] No new input clips. Previous intro.mp4 still available.")
            log("[4/4] To generate a new intro, add video clips to input/ and run again.")

    # Summary
    log("")
    log("=" * 55)
    log("  Done!")
    log("=" * 55)
    log("")

    if os.path.exists(intro_path):
        log(f"  Intro: {intro_path}")
    if os.path.exists(outro_path):
        log(f"  Outro: {outro_path}")

    log("")
    log("Drag both into CapCut and you're good to go!")
    log("")


if __name__ == "__main__":
    main()
