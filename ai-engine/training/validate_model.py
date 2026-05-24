#!/usr/bin/env python3
"""
Model validation — mAP, precision, recall targets (Blueprint v2.0).

Targets:
  mAP@50     > 0.92
  mAP@50-95  > 0.75
  Precision  > 0.90
  Recall     > 0.95 (critical classes prioritised)
"""

import argparse
import sys
from pathlib import Path

from ultralytics import YOLO

sys.path.insert(0, str(Path(__file__).resolve().parent))
from device_utils import get_default_device  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--weights",
        default="tower_safety/phase1_frozen/weights/best.pt",
        help="Path to trained weights",
    )
    parser.add_argument("--data", default="dataset/data.yaml")
    parser.add_argument("--conf", type=float, default=0.35)
    parser.add_argument("--iou", type=float, default=0.45)
    parser.add_argument("--device", default=get_default_device())
    args = parser.parse_args()

    model = YOLO(args.weights)
    metrics = model.val(
        data=args.data,
        split="test",
        imgsz=640,
        conf=args.conf,
        iou=args.iou,
        device=args.device,
        plots=True,
    )

    print(f"mAP@50:    {metrics.box.map50:.4f}  (target > 0.92)")
    print(f"mAP@50-95: {metrics.box.map:.4f}   (target > 0.75)")
    print(f"Precision: {metrics.box.mp:.4f}  (target > 0.90)")
    print(f"Recall:    {metrics.box.mr:.4f}  (target > 0.95)")

    for i, name in enumerate(model.names.values()):
        ap = metrics.box.ap50[i] if hasattr(metrics.box, "ap50") else metrics.box.ap[i]
        print(f"  {name}: AP@50={ap:.4f}")


if __name__ == "__main__":
    main()
