#!/usr/bin/env python3
"""
Phase 2 training — full fine-tuning (Blueprint v2.0).
Target: 88–91% accuracy with 5,000+ images and full augmentation.

Usage:
  python training/train_phase2.py --weights tower_safety/phase1_frozen/weights/best.pt
"""

import argparse
import sys
from pathlib import Path

from ultralytics import YOLO

sys.path.insert(0, str(Path(__file__).resolve().parent))
from device_utils import get_default_device  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Tower AI — Phase 2 full fine-tuning")
    parser.add_argument(
        "--weights",
        default="tower_safety/phase1_frozen/weights/best.pt",
        help="Checkpoint from Phase 1",
    )
    parser.add_argument("--data", default="dataset/data.yaml")
    parser.add_argument("--epochs", type=int, default=200)
    parser.add_argument("--batch", type=int, default=8)
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--device", default=get_default_device())
    args = parser.parse_args()

    print(f"Using device: {args.device}")
    model = YOLO(args.weights)
    model.train(
        data=args.data,
        epochs=args.epochs,
        imgsz=args.imgsz,
        batch=args.batch,
        lr0=0.0001,
        lrf=0.01,
        momentum=0.937,
        weight_decay=0.0005,
        warmup_epochs=5,
        mosaic=1.0,
        mixup=0.2,
        copy_paste=0.3,
        degrees=10.0,
        optimizer="SGD",
        cos_lr=True,
        amp=True,
        device=args.device,
        project="tower_safety",
        name="phase2_full",
        patience=40,
    )
    print("Phase 2 complete. Best weights: tower_safety/phase2_full/weights/best.pt")


if __name__ == "__main__":
    main()
