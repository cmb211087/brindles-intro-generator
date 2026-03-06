"""Outro builder - generates a static branded outro card.

Layout (1920x1080, 18 seconds):
  - Gradient blue background (darker at edges)
  - Large Brindles logo centered in upper portion
  - Thin white separator line
  - "Subscribe to The Brindles!" text below
  - Lower 40% kept clear for YouTube end screen elements
  - Outro music with fade-out
"""

import os

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy import (
    ColorClip, ImageClip,
    CompositeVideoClip, AudioFileClip,
)
from moviepy.video.fx.CrossFadeIn import CrossFadeIn
from moviepy.audio.fx.AudioFadeOut import AudioFadeOut

from src.config import (
    BRAND_COLOR, RESOLUTION, FPS,
    OUTRO_DURATION, OUTRO_MUSIC_FADE_OUT,
    LOGO_PATH, OUTRO_MUSIC_PATH, FONT_PATH, OUTPUT_DIR,
)


def _make_gradient_bg(duration):
    """Create a radial gradient background - lighter center, darker edges."""
    w, h = RESOLUTION
    # Build a single gradient frame
    y_coords, x_coords = np.mgrid[0:h, 0:w]
    cx, cy = w / 2, h / 2
    # Normalized distance from center (0 at center, 1 at corners)
    dist = np.sqrt((x_coords - cx) ** 2 + (y_coords - cy) ** 2)
    dist = dist / dist.max()

    # Brand color center, darker at edges
    r0, g0, b0 = BRAND_COLOR  # (43, 94, 167)
    darken = 0.55  # edge brightness multiplier
    frame = np.zeros((h, w, 3), dtype=np.uint8)
    for i, c in enumerate([r0, g0, b0]):
        frame[:, :, i] = (c * (1 - dist * (1 - darken))).astype(np.uint8)

    return ImageClip(frame).with_duration(duration)


def _render_text_image(text, font_size, color=(255, 255, 255, 255), font_path=FONT_PATH):
    """Render text to a PIL RGBA image with generous padding. No clipping."""
    font = ImageFont.truetype(font_path, font_size)
    # Measure text with a dummy draw
    dummy = Image.new("RGBA", (1, 1), (0, 0, 0, 0))
    draw = ImageDraw.Draw(dummy)
    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    # Add generous padding
    pad = font_size
    img_w = text_w + pad * 2
    img_h = text_h + pad * 2
    img = Image.new("RGBA", (img_w, img_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    # Draw centered in the padded image
    x = (img_w - text_w) // 2 - bbox[0]
    y = (img_h - text_h) // 2 - bbox[1]
    draw.text((x, y), text, font=font, fill=color)
    return img


def build_outro(output_path=None, progress_fn=None):
    """Build the static outro video."""
    output_path = output_path or os.path.join(OUTPUT_DIR, "outro.mp4")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    if progress_fn:
        progress_fn("  Creating outro background...")

    # Gradient background
    bg = _make_gradient_bg(OUTRO_DURATION)
    layers = [bg]

    # Logo - large and centered in upper portion
    logo_size = 280
    logo_y = 100
    if os.path.exists(LOGO_PATH):
        logo_raw = ImageClip(LOGO_PATH)
        orig_w = logo_raw.size[0]
        scale = logo_size / orig_w
        logo = logo_raw.resized(scale)
        logo = logo.with_duration(OUTRO_DURATION)
        logo = logo.with_position(("center", logo_y))
        layers.append(logo)
        bottom_of_logo = logo_y + logo_size
    else:
        txt_img = _render_text_image("The Brindles", 90)
        txt_clip = ImageClip(np.array(txt_img)).with_duration(OUTRO_DURATION)
        txt_clip = txt_clip.with_position(("center", logo_y + 80))
        layers.append(txt_clip)
        bottom_of_logo = logo_y + 200

    if progress_fn:
        progress_fn("  Adding subscribe text...")

    # Separator line
    sep_y = bottom_of_logo + 30
    sep_img = Image.new("RGBA", (400, 3), (255, 255, 255, 180))
    sep = ImageClip(np.array(sep_img)).with_duration(OUTRO_DURATION)
    sep = sep.with_position(("center", sep_y))
    layers.append(sep)

    # Subscribe text - rendered via PIL to avoid MoviePy TextClip clipping
    sub_y = sep_y + 35
    sub_img = _render_text_image("Subscribe to The Brindles!", 48)
    subscribe = ImageClip(np.array(sub_img)).with_duration(OUTRO_DURATION)
    subscribe = subscribe.with_position(("center", sub_y))
    layers.append(subscribe)

    # Tagline
    tag_y = sub_y + 80
    tag_img = _render_text_image("Adventures & Football & Home", 26, color=(200, 215, 235, 255))
    tagline = ImageClip(np.array(tag_img)).with_duration(OUTRO_DURATION)
    tagline = tagline.with_position(("center", tag_y))
    layers.append(tagline)

    # Compose all layers
    final = CompositeVideoClip(layers, size=RESOLUTION)
    final = final.with_duration(OUTRO_DURATION)

    # Fade in from black
    final = final.with_effects([CrossFadeIn(0.5)])

    # Add outro music
    if os.path.exists(OUTRO_MUSIC_PATH):
        if progress_fn:
            progress_fn("  Adding outro music...")

        music = AudioFileClip(OUTRO_MUSIC_PATH)
        if music.duration > OUTRO_DURATION:
            music = music.subclipped(0, OUTRO_DURATION)
        music = music.with_effects([AudioFadeOut(OUTRO_MUSIC_FADE_OUT)])
        final = final.with_audio(music)

    # Export
    if progress_fn:
        progress_fn("  Rendering outro video...")

    final.write_videofile(
        output_path,
        codec="libx264",
        audio_codec="aac",
        fps=FPS,
        preset="medium",
        logger=None,
    )

    final.close()

    if progress_fn:
        progress_fn(f"  Outro saved: {output_path} ({OUTRO_DURATION:.0f} seconds)")

    return output_path
