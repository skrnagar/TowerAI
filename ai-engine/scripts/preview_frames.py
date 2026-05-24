#!/usr/bin/env python3
"""Quick preview: run YOLO COCO pretrained on a sample frame (smoke test before custom training)."""

import argparse
from pathlib import Path

from ultralytics import YOLO


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--frame",
        type=Path,
        help="Path to a single frame image",
    )
    parser.add_argument(
        "--model",
        default="yolov8n.pt",
        help="Pretrained weights (downloads automatically)",
    )
    args = parser.parse_args()

    frames_dir = Path(__file__).resolve().parents[1] / "dataset" / "raw" / "frames"
    if args.frame:
        image = args.frame
    else:
        candidates = sorted(frames_dir.rglob("*.jpg"))
        if not candidates:
            print("No frames found. Run extract_frames.py first.")
            return
        image = candidates[0]

    print(f"Running {args.model} on {image}")
    model = YOLO(args.model)
    results = model(str(image), conf=0.35)
    out = Path(__file__).resolve().parents[1] / "dataset" / "raw" / "preview.jpg"
    results[0].save(str(out))
    print(f"Saved preview: {out}")


if __name__ == "__main__":
    main()
