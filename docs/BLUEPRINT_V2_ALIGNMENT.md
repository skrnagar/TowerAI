# Blueprint v2.0 — Repository Alignment

This document maps the **AI Tower Safety System Technical Blueprint v2.0** to the Tower AI monorepo implementation.

---

## Five-Layer Architecture

| Blueprint Layer | Monorepo Location | Notes |
|-----------------|-------------------|-------|
| Camera & Edge | `ai-engine/app/services/rtsp_processor.py` | RTSP, buffer size=1 for low latency |
| AI Inference | `ai-engine/app/services/inference.py`, `ensemble.py`, `tracker.py` | YOLOv8x primary; ensemble Phase 3 |
| Backend Services | `backend/app/` | FastAPI, Celery, WebSocket |
| Data Layer | `infrastructure/postgres/`, Redis, MinIO | InfluxDB/FAISS — Phase 3+ |
| Presentation | `frontend/src/` | Next.js 15 dashboard |

---

## AI Model — 8 Detection Classes

| ID | Class | Priority | Confidence Threshold | Implemented |
|----|-------|----------|-------------------|-------------|
| 0 | helmet_on | CRITICAL | 0.55 | Yes |
| 1 | helmet_off | CRITICAL | 0.35 | Yes |
| 2 | harness_on | CRITICAL | 0.55 | Yes |
| 3 | harness_off | CRITICAL | 0.35 | Yes |
| 4 | person_tower | HIGH | 0.40 | Yes |
| 5 | unsafe_climbing | HIGH | 0.45 | Yes |
| 6 | restricted_zone | HIGH | 0.50 | Yes |
| 7 | lifeline_attached | MEDIUM | 0.60 | Flagged Phase 3+ |

Config: `ai-engine/app/core/constants.py`  
Dataset: `ai-engine/dataset/data.yaml`

**Model change from Step 1:** Blueprint specifies **YOLOv8x** (not YOLOv11). Training scripts use Ultralytics `yolov8x.pt`.

---

## Post-Processing Stack

| Technique | File | Phase |
|-----------|------|-------|
| Per-class thresholds | `constants.py` | 1 |
| Temporal 5/15 filter | `temporal_filter.py` | 1 |
| DeepSORT tracking | `tracker.py` | 1 (IOU placeholder → full DeepSORT Step 9) |
| WBF ensemble | `ensemble.py` | 3 |
| VLM verifier | `prompts/vlm_secondary_verifier.json` | 4 |
| Pose estimation | `yolov8-pose` config flag | 3 |

---

## Prompt Library

| Prompt | Path |
|--------|------|
| Annotator labelling | `ai-engine/prompts/annotator_labelling.txt` |
| VLM secondary verifier | `ai-engine/prompts/vlm_secondary_verifier.json` |
| Alert generation | `ai-engine/prompts/alert_generation.json` |
| Chain-of-thought safety | `ai-engine/prompts/chain_of_thought_safety.txt` |
| Backend loader | `backend/app/services/prompts.py` |

Additional prompts (daily report, incident investigation, active learning, policy Q&A, camera placement) — see `docs/PROMPT_LIBRARY.md`.

---

## Training Pipeline

```bash
# Phase 1 — frozen backbone (50 epochs)
python ai-engine/training/train_phase1.py --data ai-engine/dataset/data.yaml

# Phase 2 — full fine-tune (200 epochs)
python ai-engine/training/train_phase2.py

# Validation
python ai-engine/training/validate_model.py

# Jetson TensorRT export
python ai-engine/training/export_tensorrt.py
```

---

## Alerts & Notifications

| Channel | Implementation | Phase |
|---------|----------------|-------|
| Dashboard WebSocket | `backend/app/websocket/manager.py` | 1 |
| WhatsApp (Twilio) | `backend/app/utils/notifier.py` | 2 |
| Email / SMS | Celery tasks (stub) | 2 |
| Webhook | `notifier.send_webhook()` | 2 |

---

## MVP Scope vs Blueprint

| Blueprint Feature | MVP (Phase 1) | Later |
|-------------------|---------------|-------|
| 8-class YOLO | Architecture + training scripts | Trained weights from client data |
| YOLOv8x | Yes | — |
| Ensemble YOLOv8x+YOLOv9e | Stub only | Phase 3 |
| Pose estimation | Config flag off | Phase 3 |
| Vision-LLM verifier | Prompts ready | Phase 4 |
| Lifeline detection | Disabled (`LIFELINE_ENABLED=False`) | Phase 3+ |
| InfluxDB / FAISS | Not in docker-compose | Phase 3+ |
| Mobile PWA | Not started | Phase 2+ |

---

## Budget & Timeline (from Blueprint)

- **MVP budget:** Rs. 55,000
- **Week 1:** Data collection, labelling, Phase 1 training
- **Week 2:** Phase 2 training, backend, dashboard, cameras
- **Week 3:** Ensemble prep, alerts, E2E demo
- **Months 2–6:** Accuracy phases 3–5 toward 99%

---

## Next Engineering Actions

1. Collect client tower videos and begin Roboflow/CVAT labelling using `annotator_labelling.txt`
2. Run `train_phase1.py` → `train_phase2.py` when dataset ready
3. Copy `best.pt` to `/models/tower_safety/` in AI engine container
4. **Step 2:** `make build && make up` — verify Docker stack
5. Connect first RTSP camera and validate 5 FPS inference + 5/15 temporal alerts
