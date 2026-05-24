#!/usr/bin/env python3
"""
Extract frames from downloaded videos for labelling and training.

Blueprint v2.0: 1 FPS extraction (~500–1000 images per 10 min video).

Usage:
  python scripts/extract_frames.py
  python scripts/extract_frames.py --fps 1 --max-frames 500
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import cv2

VIDEO_DIR = Path(__file__).resolve().parents[1] / "dataset" / "raw" / "videos"
FRAMES_DIR = Path(__file__).resolve().parents[1] / "dataset" / "raw" / "frames"
MANIFEST_PATH = FRAMES_DIR / "manifest.json"


def extract_from_video(
    video_path: Path,
    output_dir: Path,
    fps: float = 1.0,
    max_frames: int | None = None,
) -> list[dict]:
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open video: {video_path}")

    native_fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    frame_interval = max(1, int(round(native_fps / fps)))
    video_id = video_path.stem
    out_subdir = output_dir / video_id
    out_subdir.mkdir(parents=True, exist_ok=True)

    entries: list[dict] = []
    frame_idx = 0
    saved = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if frame_idx % frame_interval == 0:
            name = f"{video_id}_f{frame_idx:06d}.jpg"
            out_path = out_subdir / name
            cv2.imwrite(str(out_path), frame, [cv2.IMWRITE_JPEG_QUALITY, 92])
            entries.append(
                {
                    "video_id": video_id,
                    "frame_index": frame_idx,
                    "path": str(out_path.relative_to(output_dir.parent.parent)),
                    "source_video": video_path.name,
                }
            )
            saved += 1
            if max_frames and saved >= max_frames:
                break

        frame_idx += 1

    cap.release()
    print(f"  {video_id}: {saved} frames @ {fps} FPS (source {native_fps:.1f} FPS)")
    return entries


def split_dataset(
    frame_paths: list[Path],
    train_ratio: float = 0.7,
    val_ratio: float = 0.2,
) -> dict[str, list[str]]:
    """Assign frames to train/val/test by video ID (no leakage across splits)."""
    by_video: dict[str, list[Path]] = {}
    for p in frame_paths:
        vid = p.parent.name
        by_video.setdefault(vid, []).append(p)

    video_ids = sorted(by_video.keys())
    n = len(video_ids)
    n_train = max(1, int(n * train_ratio))
    n_val = max(1, int(n * val_ratio)) if n > 2 else 0

    train_vids = set(video_ids[:n_train])
    val_vids = set(video_ids[n_train : n_train + n_val])
    test_vids = set(video_ids[n_train + n_val :])

    splits: dict[str, list[str]] = {"train": [], "val": [], "test": []}
    for vid, paths in by_video.items():
        if vid in train_vids:
            key = "train"
        elif vid in val_vids:
            key = "val"
        else:
            key = "test"
        splits[key].extend([str(p) for p in paths])

    return splits


def copy_to_yolo_layout(frames_root: Path, splits_manifest: dict[str, list[str]]) -> None:
    """Copy frames into dataset/images/{train,val,test} for labelling export."""
    import shutil

    base = frames_root.parent.parent  # dataset/
    for split, paths in splits_manifest.items():
        dest_dir = base / "images" / split
        dest_dir.mkdir(parents=True, exist_ok=True)
        labels_dir = base / "labels" / split
        labels_dir.mkdir(parents=True, exist_ok=True)

        for rel in paths:
            src = frames_root.parent / rel if not Path(rel).is_absolute() else Path(rel)
            if not src.exists():
                src = frames_root / Path(rel).name
            if not src.exists():
                continue
            # paths in manifest are relative to dataset/
            full = base / rel if (base / rel).exists() else src
            if full.exists():
                shutil.copy2(full, dest_dir / full.name)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=VIDEO_DIR)
    parser.add_argument("--output", type=Path, default=FRAMES_DIR)
    parser.add_argument("--fps", type=float, default=1.0, help="Extraction rate (default 1 FPS)")
    parser.add_argument("--max-frames", type=int, default=None, help="Max frames per video")
    parser.add_argument("--layout", action="store_true", help="Copy into images/train|val|test")
    args = parser.parse_args()

    videos = sorted(args.input.glob("*.mp4"))
    videos = [v for v in videos if v.stat().st_size > 100_000]  # skip tiny/corrupt
    if not videos:
        print(f"No videos in {args.input}. Run: python scripts/download_videos.py")
        return

    args.output.mkdir(parents=True, exist_ok=True)
    all_entries: list[dict] = []

    print(f"Extracting from {len(videos)} video(s) at {args.fps} FPS...")
    for video in sorted(videos):
        all_entries.extend(
            extract_from_video(video, args.output, fps=args.fps, max_frames=args.max_frames)
        )

    frame_files = list(args.output.rglob("*.jpg"))
    splits = split_dataset(frame_files)

    manifest = {
        "total_frames": len(all_entries),
        "videos": [v.name for v in videos],
        "fps_extracted": args.fps,
        "splits": {k: len(v) for k, v in splits.items()},
        "frames": all_entries,
    }
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2))

    print(f"\nTotal frames: {len(all_entries)}")
    print(f"Split: train={len(splits['train'])} val={len(splits['val'])} test={len(splits['test'])}")
    print(f"Manifest: {MANIFEST_PATH}")

    if args.layout:
        copy_to_yolo_layout(args.output, splits)
        print("Copied to dataset/images/{train,val,test}/ — add labels in dataset/labels/")

    print("\nNext steps:")
    print("  1. Label frames in Roboflow/CVAT (see prompts/annotator_labelling.txt)")
    print("  2. Export YOLO format into dataset/images + dataset/labels")
    print("  3. python training/train_phase1.py")


if __name__ == "__main__":
    main()
