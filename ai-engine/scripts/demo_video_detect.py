#!/usr/bin/env python3
"""
Run YOLO on a local video file and POST violations to the backend API.
Use for tracing detections / accuracy before RTSP cameras are wired.

  cd ai-engine
  python3 scripts/demo_video_detect.py --video dataset/raw/videos/K6YHA3p3APM.f136.mp4 --max-frames 60
"""

from __future__ import annotations

import argparse
import base64
import sys
from datetime import datetime, timezone
from pathlib import Path

import cv2
import httpx

# Demo site/camera from infrastructure/postgres/init.sql seed
SITE_ID = "a0000000-0000-0000-0000-000000000001"
CAMERA_ID = "c0000000-0000-0000-0000-000000000001"
BACKEND_URL = "http://127.0.0.1:8000"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--video", required=True, help="Path to .mp4")
    parser.add_argument("--max-frames", type=int, default=30)
    parser.add_argument("--backend", default=BACKEND_URL)
    parser.add_argument("--model", default="yolov8n.pt")
    parser.add_argument("--out-dir", default="dataset/demo_output")
    args = parser.parse_args()

    video_path = Path(args.video)
    if not video_path.is_file():
        print(f"Video not found: {video_path}", file=sys.stderr)
        return 1

    try:
        from ultralytics import YOLO
    except ImportError:
        print("Install: pip install -r requirements.txt", file=sys.stderr)
        return 1

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    model = YOLO(args.model)
    cap = cv2.VideoCapture(str(video_path))
    frame_idx = 0
    posted = 0

    with httpx.Client(timeout=30.0) as client:
        while frame_idx < args.max_frames:
            ok, frame = cap.read()
            if not ok:
                break

            results = model.predict(frame, verbose=False, conf=0.35)
            boxes = []
            for r in results:
                for box in r.boxes:
                    cls_id = int(box.cls[0])
                    name = r.names.get(cls_id, str(cls_id))
                    x1, y1, x2, y2 = box.xyxy[0].tolist()
                    h, w = frame.shape[:2]
                    boxes.append(
                        {
                            "class": name,
                            "x": x1 / w,
                            "y": y1 / h,
                            "w": (x2 - x1) / w,
                            "h": (y2 - y1) / h,
                            "confidence": float(box.conf[0]),
                        }
                    )

            if not boxes:
                frame_idx += 1
                continue

            # Save annotated frame for accuracy review
            annotated = results[0].plot()
            shot_path = out_dir / f"frame_{frame_idx:05d}.jpg"
            cv2.imwrite(str(shot_path), annotated)

            # Map COCO person -> demo violation for pipeline test
            violation_type = "helmet_off"
            severity = "high"
            confidence = max(b["confidence"] for b in boxes)

            payload = {
                "camera_id": CAMERA_ID,
                "site_id": SITE_ID,
                "violation_type": violation_type,
                "severity": severity,
                "confidence": confidence,
                "bounding_boxes": boxes,
                "frame_timestamp": datetime.now(timezone.utc).isoformat(),
                "screenshot_key": str(shot_path.name),
                "metadata": {"source": "demo_video_detect", "frame": frame_idx},
            }

            try:
                resp = client.post(f"{args.backend.rstrip('/')}/api/v1/violations", json=payload)
                if resp.status_code == 201:
                    posted += 1
                    print(f"frame {frame_idx}: posted violation ({len(boxes)} boxes) → {shot_path}")
                else:
                    print(f"frame {frame_idx}: API {resp.status_code} {resp.text[:200]}")
            except httpx.ConnectError:
                print("Backend not running. Start: cd backend && source .venv/bin/activate && uvicorn app.main:app --port 8000")
                return 1

            frame_idx += 1

    cap.release()
    print(f"\nDone. Frames processed: {frame_idx}, violations posted: {posted}")
    print(f"Screenshots: {out_dir.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
