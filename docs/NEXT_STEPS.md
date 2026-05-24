# What To Do Next — Tower AI

Based on your current terminal state (May 2026).

---

## Where you are now

| Area | Status |
|------|--------|
| Frontend | Running at http://localhost:3000 |
| Supabase CLI | Linked to `edwdhyoghxnqrgzrocol` |
| Frames extracted | 783 train + 6 test images |
| Labels | **0** — training blocked until labelled |
| Training | Failed on `device=0` (no CUDA on Mac) — **fixed** to auto `mps`/`cpu` |
| Preview inference | Works (`preview.jpg` saved) |
| Missing videos | 2 of 4 (disk was full) |

---

## Priority 1 — Label the dataset (required)

Training cannot run without `.txt` label files in `dataset/labels/train/`.

1. Open [Roboflow](https://roboflow.com) (free tier) or CVAT  
2. Upload `ai-engine/dataset/images/train/` (start with 100–200 frames)  
3. Label 8 classes using `ai-engine/prompts/annotator_labelling.txt`  
4. Export **YOLOv8** format → unzip into:
   - `dataset/images/train` + `dataset/labels/train`
   - `dataset/images/val` + `dataset/labels/val` (optional small set)

Verify:

```bash
cd ai-engine
python3 scripts/check_dataset.py
```

---

## Priority 2 — Train on your Mac

After labels exist:

```bash
cd ai-engine
python3 scripts/check_dataset.py

# Smaller model recommended on Mac (faster than yolov8x)
python3 training/train_phase1.py --data dataset/data.yaml --model yolov8n.pt --epochs 30 --batch 4

python3 training/train_phase2.py --epochs 50 --batch 4

python3 training/validate_model.py --weights tower_safety/phase2_full/weights/best.pt
```

Device is auto-selected: **MPS** on Apple Silicon, else **CPU**.

Optional SSL fix for Python 3.13 on macOS:

```bash
/Applications/Python\ 3.13/Install\ Certificates.command
```

---

## Priority 3 — Push database to Supabase

Schema is in `infrastructure/postgres/init.sql`. Apply to cloud:

**Option A — SQL Editor (fastest)**  
1. Supabase Dashboard → SQL → New query  
2. Paste contents of `infrastructure/postgres/init.sql`  
3. Run  

**Option B — CLI migration**

```bash
cd "/Users/sunil/Code/KEC TowerAI"
supabase db push
```

(After adding migration under `supabase/migrations/`)

Set backend `.env`:

```
DATABASE_URL=postgresql+asyncpg://postgres.[PASSWORD]@aws-0-[region].pooler.supabase.com:6543/postgres
```

Use **Session pooler** URI from Supabase → Project Settings → Database.

---

## Priority 4 — Run full stack

```bash
cp .env.example .env
# Edit DATABASE_URL, Supabase keys

make build && make up
```

Or locally:

```bash
# Terminal 1 — backend
cd backend && pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Terminal 2 — frontend (already running)
cd frontend && npm run dev
```

Login: `admin@towerai.local` / `Admin@123` (after DB seed).

---

## Priority 5 — Finish video dataset

Free **3–5 GB** disk, then:

```bash
brew install ffmpeg
cd ai-engine
python3 scripts/download_videos.py
python3 scripts/extract_frames.py --layout
```

---

## Quick reference — errors you hit

| Error | Fix |
|-------|-----|
| `Invalid CUDA device=0` | Use updated scripts (auto `mps`/`cpu`) or `--device mps` |
| `best.pt` not found | Train phase 1 first; validate uses phase1 weights by default now |
| `supabase link` privileges | Log in with account that **owns** the project (you fixed on 2nd login) |
| DB version warning | `supabase/config.toml` → `major_version = 17` (done) |
| Next.js lockfile warning | `outputFileTracingRoot` in `next.config.ts` (done) |
| No labels | Label in Roboflow — **main blocker** |

---

## Suggested timeline (this week)

| Day | Task |
|-----|------|
| 1 | Label 150–200 train frames in Roboflow |
| 2 | Phase 1 train + validate; push Supabase schema |
| 3 | Start backend + connect dashboard to API |
| 4 | Re-download remaining 2 videos, extract frames |
| 5 | Label more frames; Phase 2 fine-tune |

---

## Single “do this now” command

```bash
cd "/Users/sunil/Code/KEC TowerAI/ai-engine" && python3 scripts/check_dataset.py
```

If it says **no labels** → open Roboflow and start labelling. That is the critical path.
