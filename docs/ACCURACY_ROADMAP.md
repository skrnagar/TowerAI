# Accuracy Roadmap — 80% to 99%

Blueprint v2.0 | Tower AI Safety Monitoring System

> **Key insight:** ~70% of accuracy comes from data quality. A diverse, well-labelled dataset of 5,000+ images outperforms a complex model on 500 poor images.

---

## Milestone Summary

| Phase | Target Accuracy | Timeline | Status |
|-------|-----------------|----------|--------|
| Phase 1 — MVP | 80–85% | Weeks 1–3 | In progress |
| Phase 2 — Optimised | 88–91% | Weeks 4–6 | Planned |
| Phase 3 — Ensemble | 93–95% | Month 2 | Planned |
| Phase 4 — Vision-LLM | 96–97% | Month 3 | Planned |
| Phase 5 — Production | 98–99% | Months 4–6 | Planned |

---

## Phase 1 — MVP (80–85%)

**Techniques**
- YOLOv8m or YOLOv8x on ~2,000 labelled images
- Basic augmentation (flip, HSV, mosaic)
- Single-model inference
- Temporal filter 5/15 frames
- Per-class confidence thresholds (recall-first on critical classes)

**Repo assets**
- `ai-engine/training/train_phase1.py`
- `ai-engine/dataset/data.yaml`
- `ai-engine/app/services/temporal_filter.py`

**Validation targets (test set)**

| Metric | Target |
|--------|--------|
| mAP@50 | > 0.80 |
| Recall (helmet_off) | > 0.90 |
| Recall (harness_off) | > 0.90 |

---

## Phase 2 — Optimised (88–91%)

**Techniques**
- YOLOv8x full fine-tuning (200 epochs)
- 5,000+ labelled images
- Full augmentation pipeline (mixup, copy-paste, night simulation)
- Hyperparameter tuning (`model.tune()`)
- Per-class threshold tuning on validation set

**Repo assets**
- `ai-engine/training/train_phase2.py`
- `ai-engine/training/validate_model.py`

**Validation targets**

| Metric | Target |
|--------|--------|
| mAP@50 | > 0.92 |
| mAP@50-95 | > 0.75 |
| Precision | > 0.90 |
| Recall | > 0.95 |

---

## Phase 3 — Ensemble (93–95%)

**Techniques**
- YOLOv8x + YOLOv9e Weighted Box Fusion
- DeepSORT / ByteTrack tracking
- YOLOv8-Pose secondary signal for `unsafe_climbing`
- Active learning on false positives/negatives

**Repo assets**
- `ai-engine/app/services/ensemble.py`
- Set `AI_ENSEMBLE_ENABLED=true` in `.env`

---

## Phase 4 — Vision-LLM (96–97%)

**Techniques**
- GPT-4V / Claude Vision on frames with confidence < 0.70
- Chain-of-thought safety reasoning
- Human-in-the-loop feedback on disputed cases

**Repo assets**
- `ai-engine/prompts/vlm_secondary_verifier.json`
- `ai-engine/prompts/chain_of_thought_safety.txt`
- `VLM_VERIFIER_ENABLED=true`

---

## Phase 5 — 99% Target (98–99%)

**Techniques**
- 10,000+ site-specific images (client towers, lighting, PPE colours)
- 3-model ensemble + test-time augmentation (TTA)
- Continuous active learning from production false cases
- 6-month feedback loop with field supervisors

---

## Per-Class Recall Targets (Production)

| Class | Target Recall | Target Precision | Strategy |
|-------|---------------|------------------|----------|
| helmet_off | >98% | >85% | Low threshold (0.35), temporal filter |
| harness_off | >98% | >85% | Same — life-safety priority |
| unsafe_climbing | >92% | >88% | Pose estimation + YOLO class |
| restricted_zone | >95% | >90% | Polygon zones + detection |
| person_tower | >97% | >92% | Base worker detection |

---

## Data Collection Checklist

- [ ] 6–7 tower work videos (1080p+, day + night)
- [ ] Frame extraction at 1 FPS (~500–1000 images per 10 min video)
- [ ] Open-source supplements: COCO Person, Safety Helmet (Kaggle), Roboflow PPE
- [ ] Negative samples: empty towers, partial occlusions
- [ ] Target: 8,000 raw images → 5,600 train / 1,600 val / 800 test

See `ai-engine/prompts/annotator_labelling.txt` for labelling rules.
