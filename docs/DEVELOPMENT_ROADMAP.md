# Development Roadmap — Phase 1 MVP

## Tower AI Safety Monitoring System

---

## Overview

15-step implementation plan for Phase 1 MVP. Each step builds on the previous, delivering incremental value.

**Legend**: ✅ Complete | 🔧 In Progress | ⬜ Pending

---

## Step 1 — Project Architecture ✅

**Deliverables**:
- [x] Monorepo folder structure
- [x] Docker Compose multi-service setup
- [x] Backend, frontend, AI engine skeletons
- [x] PostgreSQL schema with seed data
- [x] Nginx reverse proxy configuration
- [x] Environment configuration template
- [x] Architecture documentation

**Files Created**: 60+ foundation files across all services.

---

## Step 2 — Docker Monorepo Setup ⬜

**Goal**: Verify all services start and communicate.

**Tasks**:
- [ ] Build all Docker images (`make build`)
- [ ] Start full stack (`make up`)
- [ ] Verify health endpoints for all services
- [ ] Confirm PostgreSQL init script runs
- [ ] Confirm MinIO buckets created
- [ ] Test Nginx routing (frontend, API, WebSocket)

**Acceptance Criteria**:
- All 9 containers running and healthy
- `curl http://localhost/health` returns 200
- MinIO console accessible at port 9001

---

## Step 3 — FastAPI Backend Foundation ⬜

**Goal**: Production-ready API with auth working end-to-end.

**Tasks**:
- [ ] Alembic migration setup from init.sql
- [ ] JWT login flow tested
- [ ] RBAC middleware verified for all roles
- [ ] Structured logging output verified
- [ ] Error handling middleware
- [ ] API integration tests

**Acceptance Criteria**:
- `POST /api/v1/auth/login` returns valid JWT
- Protected endpoints reject unauthenticated requests
- Swagger docs accessible at `/docs`

---

## Step 4 — PostgreSQL + Redis + MinIO ⬜

**Goal**: Data layer fully operational with storage integration.

**Tasks**:
- [ ] MinIO client service in backend (upload/download)
- [ ] Redis connection pool and pub/sub setup
- [ ] Database connection pooling verified under load
- [ ] Screenshot upload pipeline (backend → MinIO)
- [ ] Redis pub/sub bridge for WebSocket

**Acceptance Criteria**:
- Upload test file to MinIO via backend API
- Redis pub/sub message delivered between services

---

## Step 5 — Next.js Frontend Dashboard ⬜

**Goal**: Functional dashboard with auth and navigation.

**Tasks**:
- [ ] Install shadcn/ui components via CLI
- [ ] Auth context/provider with token management
- [ ] Protected route middleware
- [ ] Dashboard stats fetched from API
- [ ] Responsive layout for control room displays
- [ ] Install dependencies and verify build

**Acceptance Criteria**:
- Login → Dashboard flow works
- All navigation pages render
- Stats cards show live API data

---

## Step 6 — RTSP Camera Ingestion ⬜

**Goal**: Multi-camera RTSP stream capture running reliably.

**Tasks**:
- [ ] RTSPProcessor tested with real IP camera
- [ ] Frame callback pipeline wired
- [ ] Auto-reconnect on stream failure
- [ ] Camera health check Celery task
- [ ] Backend API to register/start/stop cameras
- [ ] Camera status updates in database

**Acceptance Criteria**:
- Stable RTSP capture from at least 1 camera
- Automatic reconnect after network interruption
- Camera status reflects online/offline in dashboard

---

## Step 7 — YOLO Inference Engine ⬜

**Goal**: YOLOv11 detecting workers, helmets, and harnesses.

**Tasks**:
- [ ] Download/configure YOLOv11 model weights
- [ ] Custom model training for safety classes (or use pre-trained + fine-tune)
- [ ] GPU inference verified
- [ ] CPU fallback for development
- [ ] Confidence threshold tuning
- [ ] Inference latency benchmarking (target: <200ms GPU)

**Acceptance Criteria**:
- Detect person, helmet, no_helmet, harness, no_harness
- 5 FPS sustained inference on test stream
- Batch inference for 2+ cameras

---

## Step 8 — Worker + Helmet + Harness Detection ⬜

**Goal**: Accurate PPE compliance detection with low false positives.

**Tasks**:
- [ ] Person-helmet association logic (IoU overlap)
- [ ] Person-harness association logic
- [ ] Confidence threshold optimization per class
- [ ] Test with real tower site footage
- [ ] False positive/negative rate measurement

**Acceptance Criteria**:
- >90% helmet detection accuracy on test set
- >85% harness detection accuracy on test set
- <5% false positive rate with temporal filtering

---

## Step 9 — DeepSORT Tracking ⬜

**Goal**: Persistent worker tracking IDs across frames.

**Tasks**:
- [ ] Integrate DeepSORT library
- [ ] Replace IOU placeholder tracker
- [ ] Tracking ID persistence across occlusions
- [ ] Track cleanup for departed workers
- [ ] Tracking ID included in violation records

**Acceptance Criteria**:
- Same worker maintains ID for 30+ seconds
- Tracking survives brief occlusions
- No ID swaps between nearby workers

---

## Step 10 — Violation Rule Engine ⬜

**Goal**: All three violation types detected and logged.

**Tasks**:
- [ ] helmet_off rule with temporal filtering
- [ ] harness_off rule with temporal filtering
- [ ] restricted_zone polygon intersection
- [ ] Violation severity assignment
- [ ] Screenshot capture on violation
- [ ] POST violation to backend API

**Acceptance Criteria**:
- All 3 violation types trigger correctly
- 3-frame temporal filter prevents flicker alerts
- Screenshot stored in MinIO with violation record

---

## Step 11 — Real-Time WebSocket Streaming ⬜

**Goal**: Live detection data streamed to dashboard clients.

**Tasks**:
- [ ] Redis pub/sub → WebSocket bridge in backend
- [ ] Detection overlay messages via `/ws/cameras/{id}`
- [ ] Alert push via `/ws/alerts`
- [ ] Dashboard stats via `/ws`
- [ ] Multi-client connection management
- [ ] Heartbeat/ping-pong keepalive

**Acceptance Criteria**:
- Detection overlays appear within 500ms of inference
- Alerts pushed to all connected clients instantly
- Stable connections for 24+ hours

---

## Step 12 — Dashboard Live Feed UI ⬜

**Goal**: Camera grid with real-time detection overlays.

**Tasks**:
- [ ] WebSocket-connected camera feed components
- [ ] Canvas/SVG bounding box overlay rendering
- [ ] Alert sidebar with real-time updates
- [ ] Violation flash animation on critical alerts
- [ ] Multi-camera grid layout (1/2/4/9 grid)
- [ ] Full-screen single camera view

**Acceptance Criteria**:
- Live bounding boxes rendered on camera feeds
- Alert sidebar updates without page refresh
- 15 FPS overlay update rate

---

## Step 13 — Alert System ⬜

**Goal**: End-to-end alert lifecycle from detection to resolution.

**Tasks**:
- [ ] Celery task: violation → alert creation
- [ ] Alert notification via WebSocket
- [ ] Alert acknowledge/resolve/dismiss API
- [ ] Alert assignment to operators
- [ ] Alert sound/visual notification in UI
- [ ] Alert count badge in header

**Acceptance Criteria**:
- Violation automatically creates alert within 1 second
- Operator can acknowledge and resolve alerts
- Alert status tracked through full lifecycle

---

## Step 14 — Incident Logging ⬜

**Goal**: Complete incident records with evidence and audit trail.

**Tasks**:
- [ ] Violation record with screenshot evidence
- [ ] Incident detail page with timeline
- [ ] Audit log for all operator actions
- [ ] Export incident reports (PDF/CSV)
- [ ] Recording segment linking to violations
- [ ] Search and filter incidents

**Acceptance Criteria**:
- Every violation has screenshot evidence in MinIO
- Full audit trail for acknowledge/resolve actions
- Incident searchable by date, type, camera, worker ID

---

## Step 15 — Analytics APIs ⬜

**Goal**: Safety metrics and trend visualization.

**Tasks**:
- [ ] Violations over time API (daily/weekly/monthly)
- [ ] Compliance rate calculation
- [ ] Camera-wise violation breakdown
- [ ] Violation type distribution
- [ ] Frontend charts (Recharts)
- [ ] Date range filtering

**Acceptance Criteria**:
- Analytics page shows trend charts
- Compliance rate calculated correctly
- Data filterable by site, camera, date range

---

## Timeline Estimate

| Step | Duration | Cumulative |
|------|----------|------------|
| 1. Architecture | 1 week | Week 1 |
| 2. Docker Setup | 2 days | Week 1 |
| 3. Backend Foundation | 3 days | Week 2 |
| 4. Data Layer | 2 days | Week 2 |
| 5. Frontend Dashboard | 1 week | Week 3 |
| 6. RTSP Ingestion | 1 week | Week 4 |
| 7. YOLO Inference | 1 week | Week 5 |
| 8. PPE Detection | 1 week | Week 6 |
| 9. DeepSORT Tracking | 3 days | Week 6 |
| 10. Violation Engine | 3 days | Week 7 |
| 11. WebSocket Streaming | 3 days | Week 7 |
| 12. Live Feed UI | 1 week | Week 8 |
| 13. Alert System | 3 days | Week 8 |
| 14. Incident Logging | 3 days | Week 9 |
| 15. Analytics | 3 days | Week 9 |

**Total Phase 1 MVP**: ~9 weeks

---

## Post-Phase 1 Roadmap (Future)

| Phase | Features |
|-------|----------|
| Phase 2 | Lifeline detection, advanced pose estimation, mobile app |
| Phase 3 | Predictive analytics, face recognition (opt-in), multi-site |
| Phase 4 | Edge AI boxes, federated learning, enterprise multi-tenant |
