# Tower AI — Training Dataset

## Source videos (reference)

| # | URL | Video ID |
|---|-----|----------|
| 1 | [YouTube Short](https://www.youtube.com/shorts/vDGtISwKO2A) | `vDGtISwKO2A` |
| 2 | [youtu.be/K6YHA3p3APM](https://youtu.be/K6YHA3p3APM) | `K6YHA3p3APM` |
| 3 | [Tower work footage](https://www.youtube.com/watch?v=vrDC-Dfnnhw) | `vrDC-Dfnnhw` |
| 4 | [youtu.be/SNvZm2Vnwnc](https://youtu.be/SNvZm2Vnwnc) | `SNvZm2Vnwnc` |

Splits are **by video** (not by frame) so the same scene does not appear in train and test.

---

## Current status

| Video | Frames | Split | Status |
|-------|--------|-------|--------|
| [K6YHA3p3APM](https://youtu.be/K6YHA3p3APM) | 783 | **train** | Ready |
| [vDGtISwKO2A](https://www.youtube.com/shorts/vDGtISwKO2A) | 6 | **test** | Ready (short clip) |
| [vrDC-Dfnnhw](https://www.youtube.com/watch?v=vrDC-Dfnnhw) | — | val | Re-download after freeing disk |
| [SNvZm2Vnwnc](https://youtu.be/SNvZm2Vnwnc) | — | val/test | Re-download after freeing disk |

**789 frames** extracted under `dataset/raw/frames/`. Labels still required before training.

---

## Pipeline

```bash
cd ai-engine

# 1. Install tools (once)
pip install yt-dlp opencv-python-headless ultralytics

# 2. Download videos (needs ~2GB free disk; install ffmpeg for best quality)
#    brew install ffmpeg
python3 scripts/download_videos.py

# 3. Extract frames at 1 FPS → dataset/raw/frames/
python3 scripts/extract_frames.py --layout

# 4. Label in Roboflow or CVAT (8 classes — see prompts/annotator_labelling.txt)
#    Export YOLO format into:
#      dataset/images/train  dataset/labels/train
#      dataset/images/val    dataset/labels/val
#      dataset/images/test   dataset/labels/test

# 5. Train
python training/train_phase1.py --data dataset/data.yaml
python training/train_phase2.py
python training/validate_model.py
```

---

## Directory layout

```
dataset/
├── data.yaml              # Class names (8 classes)
├── raw/
│   ├── videos/            # Downloaded MP4s
│   ├── frames/            # Extracted JPGs + manifest.json
│   └── preview.jpg        # Optional smoke-test output
├── images/
│   ├── train/
│   ├── val/
│   └── test/
└── labels/
    ├── train/             # One .txt per image (YOLO format)
    ├── val/
    └── test/
```

---

## Labelling classes

See `prompts/annotator_labelling.txt` for rules.

| ID | Class |
|----|-------|
| 0 | helmet_on |
| 1 | helmet_off |
| 2 | harness_on |
| 3 | harness_off |
| 4 | person_tower |
| 5 | unsafe_climbing |
| 6 | restricted_zone |
| 7 | lifeline_attached |

Until labels exist, training will fail — use Roboflow Universe PPE datasets to pre-train if needed.
