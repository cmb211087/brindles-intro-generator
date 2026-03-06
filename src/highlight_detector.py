"""Highlight detection engine.

Finds the most exciting moments from raw footage using:
1. PySceneDetect for scene segmentation
2. Librosa for audio excitement scoring
3. OpenCV for visual motion scoring
"""

import os
import tempfile
import subprocess

import cv2
import librosa
import numpy as np
from scenedetect import open_video, SceneManager
from scenedetect.detectors import AdaptiveDetector

from src.config import (
    INPUT_DIR, VIDEO_EXTENSIONS, MIN_SCENE_DURATION, MAX_SCENE_DURATION,
    INTRO_CLIP_COUNT, INTRO_CLIP_DURATION, AUDIO_WEIGHT, VISUAL_WEIGHT,
    DIVERSITY_WINDOW, FPS,
)


def discover_clips(input_dir=None):
    """Find all video files in the input directory."""
    input_dir = input_dir or INPUT_DIR
    clips = []
    for fname in sorted(os.listdir(input_dir)):
        ext = os.path.splitext(fname)[1]
        if ext.lower() in {e.lower() for e in VIDEO_EXTENSIONS}:
            clips.append(os.path.join(input_dir, fname))
    return clips


def get_video_duration(clip_path):
    """Get video duration in seconds using ffprobe."""
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", clip_path],
            capture_output=True, text=True, timeout=30
        )
        return float(result.stdout.strip())
    except (ValueError, subprocess.TimeoutExpired):
        return 0.0


def detect_scenes(clip_path):
    """Run PySceneDetect AdaptiveDetector on a clip, return list of (start, end) in seconds."""
    video = open_video(clip_path)
    scene_manager = SceneManager()
    scene_manager.add_detector(AdaptiveDetector(
        adaptive_threshold=3.0,
        min_scene_len=int(MIN_SCENE_DURATION * FPS),
    ))
    scene_manager.detect_scenes(video)
    scene_list = scene_manager.get_scene_list()

    scenes = []
    for start_time, end_time in scene_list:
        start_sec = start_time.get_seconds()
        end_sec = end_time.get_seconds()
        duration = end_sec - start_sec
        if MIN_SCENE_DURATION <= duration <= MAX_SCENE_DURATION:
            scenes.append((clip_path, start_sec, end_sec))

    # If no scenes detected, treat the entire clip as one scene (if it fits)
    if not scenes:
        dur = get_video_duration(clip_path)
        if dur >= MIN_SCENE_DURATION:
            end = min(dur, MAX_SCENE_DURATION)
            scenes.append((clip_path, 0.0, end))

    return scenes


def extract_audio_segment(clip_path, start, end):
    """Extract audio from a video segment, return (samples, sample_rate) or None."""
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        tmp_path = tmp.name

    try:
        subprocess.run(
            ["ffmpeg", "-y", "-i", clip_path, "-ss", str(start), "-to", str(end),
             "-vn", "-acodec", "pcm_s16le", "-ar", "22050", "-ac", "1",
             tmp_path],
            capture_output=True, timeout=60
        )
        y, sr = librosa.load(tmp_path, sr=22050, mono=True)
        return y, sr
    except Exception:
        return None
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


def score_audio(clip_path, start, end):
    """Score audio excitement: RMS energy peaks + onset density."""
    result = extract_audio_segment(clip_path, start, end)
    if result is None or len(result[0]) == 0:
        return 0.0

    y, sr = result
    if len(y) < sr * 0.1:  # Less than 0.1 seconds of audio
        return 0.0

    # RMS energy
    rms = librosa.feature.rms(y=y, frame_length=2048, hop_length=512)[0]
    rms_score = float(np.mean(rms)) if len(rms) > 0 else 0.0

    # Onset strength (sudden changes - laughter, cheering)
    try:
        onset_env = librosa.onset.onset_strength(y=y, sr=sr)
        onset_score = float(np.mean(onset_env)) if len(onset_env) > 0 else 0.0
    except Exception:
        onset_score = 0.0

    # Weighted combination: 60% RMS, 40% onset density
    return 0.6 * rms_score + 0.4 * onset_score


def score_visual(clip_path, start, end):
    """Score visual motion using optical flow magnitude."""
    cap = cv2.VideoCapture(clip_path)
    if not cap.isOpened():
        return 0.0

    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    cap.set(cv2.CAP_PROP_POS_FRAMES, int(start * fps))

    # Sample every 0.5 seconds
    sample_interval = int(fps * 0.5)
    end_frame = int(end * fps)
    flow_magnitudes = []
    prev_gray = None
    frame_idx = int(start * fps)

    while frame_idx < end_frame:
        ret, frame = cap.read()
        if not ret:
            break

        if (frame_idx - int(start * fps)) % sample_interval == 0:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            # Resize for speed
            gray = cv2.resize(gray, (320, 180))

            if prev_gray is not None:
                flow = cv2.calcOpticalFlowFarneback(
                    prev_gray, gray, None,
                    pyr_scale=0.5, levels=3, winsize=15,
                    iterations=3, poly_n=5, poly_sigma=1.2, flags=0
                )
                mag, _ = cv2.cartToPolar(flow[..., 0], flow[..., 1])
                flow_magnitudes.append(float(np.mean(mag)))

            prev_gray = gray
        frame_idx += 1

    cap.release()

    return float(np.mean(flow_magnitudes)) if flow_magnitudes else 0.0


def normalize_scores(scores):
    """Normalize a list of scores to 0-1 range."""
    if not scores:
        return scores
    min_s = min(scores)
    max_s = max(scores)
    if max_s - min_s < 1e-10:
        return [0.5] * len(scores)
    return [(s - min_s) / (max_s - min_s) for s in scores]


def ensure_diversity(ranked_scenes, count, window=DIVERSITY_WINDOW):
    """Select top scenes ensuring no two are from the same time window in the same clip."""
    selected = []
    for scene in ranked_scenes:
        clip_path, start, end, score = scene
        # Check if too close to any already-selected scene from the same clip
        too_close = False
        for sel_clip, sel_start, sel_end, _ in selected:
            if sel_clip == clip_path and abs(start - sel_start) < window:
                too_close = True
                break
        if not too_close:
            selected.append(scene)
        if len(selected) >= count:
            break
    return selected


def find_best_window(clip_path, start, end, window_duration=INTRO_CLIP_DURATION):
    """Find the best sub-window within a scene (centered on peak audio moment)."""
    duration = end - start
    if duration <= window_duration:
        return start, end

    result = extract_audio_segment(clip_path, start, end)
    if result is None or len(result[0]) == 0:
        # Default to first window_duration seconds
        return start, start + window_duration

    y, sr = result
    # Compute RMS in small windows to find peak
    hop = 512
    rms = librosa.feature.rms(y=y, frame_length=2048, hop_length=hop)[0]
    if len(rms) == 0:
        return start, start + window_duration

    # Find peak RMS position
    peak_frame = int(np.argmax(rms))
    peak_time = librosa.frames_to_time(peak_frame, sr=sr, hop_length=hop)

    # Center window on peak
    half_win = window_duration / 2
    win_start = start + peak_time - half_win
    win_start = max(start, win_start)
    win_start = min(win_start, end - window_duration)
    win_end = win_start + window_duration

    return win_start, win_end


def detect_highlights(input_dir=None, clip_count=INTRO_CLIP_COUNT, progress_fn=None):
    """Main highlight detection pipeline.

    Returns list of (clip_path, start_time, end_time) tuples for the top highlights.
    """
    clips = discover_clips(input_dir)
    if not clips:
        raise FileNotFoundError(f"No video files found in {input_dir or INPUT_DIR}")

    if progress_fn:
        progress_fn(f"  Found {len(clips)} video file(s)")

    # Step 1: Scene detection
    if progress_fn:
        progress_fn("  Detecting scenes...")
    all_scenes = []
    for clip_path in clips:
        scenes = detect_scenes(clip_path)
        all_scenes.extend(scenes)

    if not all_scenes:
        raise ValueError("No valid scenes detected in any input clips")

    if progress_fn:
        progress_fn(f"  Found {len(all_scenes)} scene(s), scoring...")

    # Step 2: Score each scene
    audio_scores = []
    visual_scores = []
    for i, (clip_path, start, end) in enumerate(all_scenes):
        audio_scores.append(score_audio(clip_path, start, end))
        visual_scores.append(score_visual(clip_path, start, end))
        if progress_fn and (i + 1) % 5 == 0:
            progress_fn(f"  Scored {i + 1}/{len(all_scenes)} scenes...")

    # Step 3: Normalize and combine
    audio_norm = normalize_scores(audio_scores)
    visual_norm = normalize_scores(visual_scores)

    combined = []
    for i, (clip_path, start, end) in enumerate(all_scenes):
        score = AUDIO_WEIGHT * audio_norm[i] + VISUAL_WEIGHT * visual_norm[i]
        combined.append((clip_path, start, end, score))

    # Step 4: Rank and select with diversity
    combined.sort(key=lambda x: x[3], reverse=True)
    selected = ensure_diversity(combined, clip_count)

    if progress_fn:
        progress_fn(f"  Selected top {len(selected)} highlight(s)")

    # Step 5: Find best sub-window for each selected scene
    highlights = []
    for clip_path, start, end, score in selected:
        win_start, win_end = find_best_window(clip_path, start, end)
        highlights.append((clip_path, win_start, win_end))

    return highlights
