#!/usr/bin/env python3
"""Verify dataset is ready for YOLO training."""

from pathlib import Path

DATASET = Path(__file__).resolve().parents[1] / "dataset"
SPLITS = ("train", "val", "test")


def main() -> None:
    print("Tower AI — dataset readiness check\n")
    ok = True

    for split in SPLITS:
        images = list((DATASET / "images" / split).glob("*.jpg"))
        labels = list((DATASET / "labels" / split).glob("*.txt"))
        print(f"  {split}: {len(images)} images, {len(labels)} label files")
        if images and not labels:
            print(f"    BLOCKER: images exist but no labels in dataset/labels/{split}/")
            ok = False
        elif labels and len(labels) < len(images) * 0.9:
            print(f"    WARNING: fewer labels than images ({len(labels)} vs {len(images)})")

    if not any(list((DATASET / "images" / s).glob("*.jpg")) for s in SPLITS):
        print("\n  BLOCKER: no images found. Run: python3 scripts/extract_frames.py --layout")
        ok = False

    if ok and all(list((DATASET / "labels" / s).glob("*.txt")) for s in ("train",)):
        print("\nReady to train:")
        print("  python3 training/train_phase1.py --data dataset/data.yaml")
    elif ok:
        print("\nNext: label frames in Roboflow/CVAT, export YOLO format to dataset/labels/")
        print("See dataset/README.md and prompts/annotator_labelling.txt")
    else:
        print("\nFix blockers above before training.")


if __name__ == "__main__":
    main()
