#!/usr/bin/env python3
"""
Phase 1 training — transfer learning with frozen backbone (Blueprint v2.0).
Target: 80–85% accuracy on MVP dataset (~2,000 labelled images).

Usage:
  python training/train_phase1.py --data dataset/data.yaml --epochs 50
"""

import argparse

import sys
from pathlib import Path

from ultralytics import YOLO

sys.path.insert(0, str(Path(__file__).resolve().parent))
from device_utils import get_default_device  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Tower AI — Phase 1 frozen backbone training")
    parser.add_argument("--data", default="dataset/data.yaml", help="Path to data.yaml")
    parser.add_argument("--model", default="yolov8n.pt", help="Base pretrained weights (use yolov8n on Mac)")
    parser.add_argument("--epochs", type=int, default=50)
    parser.add_argument("--batch", type=int, default=8)
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument(
        "--device",
        default=get_default_device(),
        help="cpu | mps (Apple Silicon) | 0 (CUDA). Default: auto-detect",
    )
    args = parser.parse_args()

    print(f"Using device: {args.device}")
    model = YOLO(args.model)
    model.train(
        data=args.data,
        epochs=args.epochs,
        imgsz=args.imgsz,
        batch=args.batch,
        freeze=10,
        lr0=0.001,
        optimizer="AdamW",
        device=args.device,
        workers=8,
        project="tower_safety",
        name="phase1_frozen",
        patience=20,
        save_period=10,
    )
    print("Phase 1 complete. Best weights: tower_safety/phase1_frozen/weights/best.pt")


if __name__ == "__main__":
    main()
