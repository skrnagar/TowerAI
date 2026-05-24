#!/usr/bin/env python3
"""Export trained model to TensorRT FP16 for NVIDIA Jetson edge deployment."""

import argparse

from ultralytics import YOLO


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--weights", default="tower_safety/phase2_full/weights/best.pt")
    parser.add_argument("--imgsz", type=int, default=640)
    args = parser.parse_args()

    model = YOLO(args.weights)
    model.export(
        format="engine",
        device=0,
        half=True,
        imgsz=args.imgsz,
        workspace=4,
        simplify=True,
    )
    print("TensorRT engine exported. Load with: YOLO('best.engine')")


if __name__ == "__main__":
    main()
