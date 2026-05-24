#!/usr/bin/env python3
"""
Download tower safety training videos from YouTube.

Requires: pip install yt-dlp

Usage:
  python scripts/download_videos.py
  python scripts/download_videos.py --url "https://youtu.be/..."
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

# Client / project reference videos for Tower AI training data
DEFAULT_URLS = [
    "https://www.youtube.com/shorts/vDGtISwKO2A",
    "https://youtu.be/K6YHA3p3APM",
    "https://www.youtube.com/watch?v=vrDC-Dfnnhw",
    "https://youtu.be/SNvZm2Vnwnc",
]

OUTPUT_DIR = Path(__file__).resolve().parents[1] / "dataset" / "raw" / "videos"


def download(url: str, output_dir: Path) -> Path | None:
    output_dir.mkdir(parents=True, exist_ok=True)
    template = str(output_dir / "%(id)s.%(ext)s")

    # Single-file MP4 (no ffmpeg merge) — saves disk space
    cmd = [
        sys.executable,
        "-m",
        "yt_dlp",
        "--no-playlist",
        "-f",
        "best[height<=720][ext=mp4]/best[height<=720]/best",
        "-o",
        template,
        url,
    ]

    print(f"Downloading: {url}")
    result = subprocess.run(cmd, capture_output=False)
    if result.returncode != 0:
        print(f"Failed: {url}", file=sys.stderr)
        return None

    # Find newest mp4 matching this download
    mp4s = sorted(output_dir.glob("*.mp4"), key=lambda p: p.stat().st_mtime, reverse=True)
    return mp4s[0] if mp4s else None


def main() -> None:
    parser = argparse.ArgumentParser(description="Download YouTube videos for Tower AI dataset")
    parser.add_argument("--url", action="append", dest="urls", help="Additional video URL")
    parser.add_argument("--output", type=Path, default=OUTPUT_DIR)
    args = parser.parse_args()

    urls = list(DEFAULT_URLS)
    if args.urls:
        urls.extend(args.urls)

    try:
        import yt_dlp  # noqa: F401
    except ImportError:
        print("Installing yt-dlp...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "yt-dlp"])

    succeeded = 0
    for url in urls:
        path = download(url, args.output)
        if path:
            print(f"  Saved: {path}")
            succeeded += 1

    print(f"\nDone: {succeeded}/{len(urls)} videos in {args.output}")
    if succeeded:
        print("Next: python scripts/extract_frames.py")


if __name__ == "__main__":
    main()
