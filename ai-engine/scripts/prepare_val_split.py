#!/usr/bin/env python3
"""Create val split folders and copy ~10% of train images for YOLO path validation."""

import random
import shutil
from pathlib import Path

DATASET = Path(__file__).resolve().parents[1] / "dataset"
TRAIN_IMG = DATASET / "images" / "train"
VAL_IMG = DATASET / "images" / "val"
VAL_LBL = DATASET / "labels" / "val"
RATIO = 0.1
SEED = 42


def main() -> None:
    VAL_IMG.mkdir(parents=True, exist_ok=True)
    VAL_LBL.mkdir(parents=True, exist_ok=True)

    images = sorted(TRAIN_IMG.glob("*.jpg"))
    if not images:
        print(f"No images in {TRAIN_IMG}. Run: python3 scripts/extract_frames.py --layout")
        return

    random.seed(SEED)
    n_val = max(1, int(len(images) * RATIO))
    val_set = set(random.sample(images, n_val))

    for img in val_set:
        shutil.copy2(img, VAL_IMG / img.name)
        lbl = DATASET / "labels" / "train" / f"{img.stem}.txt"
        if lbl.exists():
            shutil.copy2(lbl, VAL_LBL / lbl.name)

    print(f"Val split: {n_val} images in {VAL_IMG}")
    print("Note: training still requires label .txt files in dataset/labels/train/")


if __name__ == "__main__":
    main()
