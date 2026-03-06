"""Intro builder - composes the final intro video from detected highlights.

Timeline:
  [0.0 - 1.0s]   "Coming up on The Brindles..." text on blue background
  [1.0 - 3.5s]   Highlight clip 1
  [3.5 - 6.0s]   Highlight clip 2
  [6.0 - 8.5s]   Highlight clip 3
  [8.5 - 11.0s]  Highlight clip 4
  [11.0 - 13.5s] Highlight clip 5
  [13.5 - 16.0s] Logo fade-in on gradient blue background
"""

import os

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy import (
    VideoFileClip, ColorClip, ImageClip,
    CompositeVideoClip, AudioFileClip, concatenate_videoclips,
)
from moviepy.video.fx.CrossFadeIn import CrossFadeIn
from moviepy.audio.fx.AudioFadeIn import AudioFadeIn
from moviepy.audio.fx.AudioFadeOut import AudioFadeOut

from src.config import (
    BRAND_COLOR, RESOLUTION, FPS,
    INTRO_CLIP_DURATION, INTRO_COMING_UP_DURATION, INTRO_LOGO_DURATION,
    INTRO_MUSIC_FADE_IN, INTRO_MUSIC_FADE_OUT,
    LOGO_PATH, INTRO_MUSIC_PATH, FONT_PATH, OUTPUT_DIR,
)


def _make_gradient_bg(duration):
    """Create a radial gradient background matching the outro."""
    w, h = RESOLUTION
    y_coords, x_coords = np.mgrid[0:h, 0:w]
    cx, cy = w / 2, h / 2
    dist = np.sqrt((x_coords - cx) ** 2 + (y_coords - cy) ** 2)
    dist = dist / dist.max()
    r0, g0, b0 = BRAND_COLOR
    darken = 0.55
    frame = np.zeros((h, w, 3), dtype=np.uint8)
    for i, c in enumerate([r0, g0, b0]):
        frame[:, :, i] = (c * (1 - dist * (1 - darken))).astype(np.uint8)
    return ImageClip(frame).with_duration(duration)


def _render_text_image(text, font_size, color=(255, 255, 255, 255)):
    """Render text to a PIL RGBA image with generous padding. No clipping."""
    font = ImageFont.truetype(FONT_PATH, font_size)
    dummy = Image.new("RGBA", (1, 1), (0, 0, 0, 0))
    draw = ImageDraw.Draw(dummy)
    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    pad = font_size
    img_w = text_w + pad * 2
    img_h = text_h + pad * 2
    img = Image.new("RGBA", (img_w, img_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    x = (img_w - text_w) // 2 - bbox[0]
    y = (img_h - text_h) // 2 - bbox[1]
    draw.text((x, y), text, font=font, fill=color)
    return img


def _create_coming_up_clip():
    """Create the 'Coming up on The Brindles...' title card."""
    bg = _make_gradient_bg(INTRO_COMING_UP_DURATION)

    layers = [bg]

    # Small logo above text
    if os.path.exists(LOGO_PATH):
        logo = ImageClip(LOGO_PATH)
        logo = logo.resized(150 / logo.size[0])
        logo = logo.with_duration(INTRO_COMING_UP_DURATION)
        logo = logo.with_position(("center", 390))
        layers.append(logo)

    txt_img = _render_text_image("Coming up on The Brindles...", 50)
    txt = ImageClip(np.array(txt_img)).with_duration(INTRO_COMING_UP_DURATION)
    txt = txt.with_position(("center", 560))
    layers.append(txt)

    clip = CompositeVideoClip(layers, size=RESOLUTION)
    clip = clip.with_duration(INTRO_COMING_UP_DURATION)
    clip = clip.with_effects([CrossFadeIn(0.3)])
    return clip


def _load_highlight_clip(clip_path, start, end):
    """Load a highlight clip, resize to 1080p, strip audio."""
    clip = VideoFileClip(clip_path)
    clip = clip.subclipped(start, min(end, clip.duration))

    # Ensure exact duration
    if clip.duration < INTRO_CLIP_DURATION:
        clip = clip.with_duration(clip.duration)
    else:
        clip = clip.with_duration(INTRO_CLIP_DURATION)

    # Resize to 1080p
    if clip.size != list(RESOLUTION):
        clip = clip.resized(RESOLUTION)

    # Strip original audio
    clip = clip.without_audio()
    return clip


def _create_logo_reveal():
    """Create logo reveal on gradient blue background with channel name."""
    bg = _make_gradient_bg(INTRO_LOGO_DURATION)

    layers = [bg]

    if os.path.exists(LOGO_PATH):
        logo = ImageClip(LOGO_PATH)
        # Large logo - 350px
        scale = 350 / logo.size[0]
        logo = logo.resized(scale)
        logo = logo.with_duration(INTRO_LOGO_DURATION)
        logo = logo.with_position(("center", 300))
        logo = logo.with_effects([CrossFadeIn(0.5)])
        layers.append(logo)
    else:
        txt_img = _render_text_image("The Brindles", 90)
        txt = ImageClip(np.array(txt_img)).with_duration(INTRO_LOGO_DURATION)
        txt = txt.with_position("center")
        layers.append(txt)

    clip = CompositeVideoClip(layers, size=RESOLUTION)
    clip = clip.with_duration(INTRO_LOGO_DURATION)
    return clip


def build_intro(highlights, output_path=None, progress_fn=None):
    """Build the intro video from highlight clips.

    Args:
        highlights: List of (clip_path, start_time, end_time) tuples.
        output_path: Output file path (default: output/intro.mp4).
        progress_fn: Optional callback for progress messages.

    Returns:
        Path to the generated intro video.
    """
    output_path = output_path or os.path.join(OUTPUT_DIR, "intro.mp4")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    if progress_fn:
        progress_fn("  Creating title card...")

    # 1. "Coming up" title card
    coming_up = _create_coming_up_clip()

    # 2. Load highlight clips
    highlight_clips = []
    for i, (clip_path, start, end) in enumerate(highlights):
        if progress_fn:
            progress_fn(f"  Loading highlight {i + 1}/{len(highlights)}...")
        try:
            clip = _load_highlight_clip(clip_path, start, end)
            highlight_clips.append(clip)
        except Exception as e:
            if progress_fn:
                progress_fn(f"  Warning: Could not load highlight {i + 1}: {e}")

    if not highlight_clips:
        raise ValueError("No highlight clips could be loaded")

    # 3. Logo reveal
    if progress_fn:
        progress_fn("  Creating logo reveal...")
    logo_reveal = _create_logo_reveal()

    # 4. Concatenate all clips with hard cuts
    all_clips = [coming_up] + highlight_clips + [logo_reveal]
    final = concatenate_videoclips(all_clips, method="compose")

    # 5. Add music
    if os.path.exists(INTRO_MUSIC_PATH):
        if progress_fn:
            progress_fn("  Adding music...")
        music = AudioFileClip(INTRO_MUSIC_PATH)
        # Trim to intro duration
        if music.duration > final.duration:
            music = music.subclipped(0, final.duration)
        else:
            # If music is shorter, it will just end early
            pass

        # Apply fade-in and fade-out
        music = music.with_effects([
            AudioFadeIn(INTRO_MUSIC_FADE_IN),
            AudioFadeOut(INTRO_MUSIC_FADE_OUT),
        ])

        final = final.with_audio(music)

    # 6. Export
    if progress_fn:
        progress_fn("  Rendering intro video...")

    final.write_videofile(
        output_path,
        codec="libx264",
        audio_codec="aac",
        fps=FPS,
        preset="medium",
        logger=None,
    )

    # Clean up
    final.close()
    for clip in highlight_clips:
        clip.close()

    total_duration = INTRO_COMING_UP_DURATION + len(highlight_clips) * INTRO_CLIP_DURATION + INTRO_LOGO_DURATION

    if progress_fn:
        progress_fn(f"  Intro saved: {output_path} ({total_duration:.0f} seconds)")

    return output_path
