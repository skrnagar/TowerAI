-- =============================================================================
-- TOWER AI SAFETY MONITORING SYSTEM
-- PostgreSQL Schema — Phase 1 MVP
-- =============================================================================

-- Extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ---------------------------------------------------------------------------
-- ENUM Types
-- ---------------------------------------------------------------------------
CREATE TYPE user_role AS ENUM ('admin', 'supervisor', 'operator', 'viewer');
CREATE TYPE camera_status AS ENUM ('online', 'offline', 'error', 'maintenance');
CREATE TYPE violation_type AS ENUM (
    'helmet_off', 'harness_off', 'restricted_zone', 'unsafe_climbing', 'lifeline_off'
);
CREATE TYPE violation_severity AS ENUM ('critical', 'high', 'medium', 'low');
CREATE TYPE alert_status AS ENUM ('pending', 'acknowledged', 'resolved', 'dismissed');
CREATE TYPE recording_status AS ENUM ('recording', 'completed', 'failed', 'archived');

-- ---------------------------------------------------------------------------
-- Sites — Physical deployment locations (tower sites, construction zones)
-- ---------------------------------------------------------------------------
CREATE TABLE sites (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name            VARCHAR(255) NOT NULL,
    code            VARCHAR(50) UNIQUE NOT NULL,
    description     TEXT,
    address         TEXT,
    latitude        DECIMAL(10, 8),
    longitude       DECIMAL(11, 8),
    timezone        VARCHAR(50) DEFAULT 'UTC',
    is_active       BOOLEAN DEFAULT TRUE,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_sites_code ON sites(code);
CREATE INDEX idx_sites_active ON sites(is_active);

-- ---------------------------------------------------------------------------
-- Users — Platform operators with RBAC
-- ---------------------------------------------------------------------------
CREATE TABLE users (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email           VARCHAR(255) UNIQUE NOT NULL,
    password_hash   VARCHAR(255) NOT NULL,
    full_name       VARCHAR(255) NOT NULL,
    role            user_role NOT NULL DEFAULT 'viewer',
    site_id         UUID REFERENCES sites(id) ON DELETE SET NULL,
    is_active       BOOLEAN DEFAULT TRUE,
    last_login_at   TIMESTAMPTZ,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_site ON users(site_id);

-- ---------------------------------------------------------------------------
-- Cameras — RTSP/IP camera registry
-- ---------------------------------------------------------------------------
CREATE TABLE cameras (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    site_id         UUID NOT NULL REFERENCES sites(id) ON DELETE CASCADE,
    name            VARCHAR(255) NOT NULL,
    code            VARCHAR(50) NOT NULL,
    rtsp_url        TEXT NOT NULL,
    location_label  VARCHAR(255),
    latitude        DECIMAL(10, 8),
    longitude       DECIMAL(11, 8),
    status          camera_status DEFAULT 'offline',
    fps             INTEGER DEFAULT 15,
    resolution      VARCHAR(20) DEFAULT '1920x1080',
    -- Restricted zone polygon stored as GeoJSON-compatible JSON array of [x,y] points (normalized 0-1)
    restricted_zones JSONB DEFAULT '[]'::jsonb,
    is_active       BOOLEAN DEFAULT TRUE,
    last_seen_at    TIMESTAMPTZ,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(site_id, code)
);

CREATE INDEX idx_cameras_site ON cameras(site_id);
CREATE INDEX idx_cameras_status ON cameras(status);
CREATE INDEX idx_cameras_active ON cameras(is_active);

-- ---------------------------------------------------------------------------
-- Violations — AI-detected safety violations
-- ---------------------------------------------------------------------------
CREATE TABLE violations (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    camera_id       UUID NOT NULL REFERENCES cameras(id) ON DELETE CASCADE,
    site_id         UUID NOT NULL REFERENCES sites(id) ON DELETE CASCADE,
    violation_type  violation_type NOT NULL,
    severity        violation_severity NOT NULL,
    confidence      DECIMAL(5, 4) NOT NULL CHECK (confidence >= 0 AND confidence <= 1),
    tracking_id     VARCHAR(100),
    -- Bounding boxes: [{class, x, y, w, h, confidence, tracking_id}]
    bounding_boxes  JSONB NOT NULL DEFAULT '[]'::jsonb,
    screenshot_url  TEXT,
    screenshot_key  VARCHAR(500),
    frame_timestamp TIMESTAMPTZ NOT NULL,
    metadata        JSONB DEFAULT '{}'::jsonb,
    is_acknowledged BOOLEAN DEFAULT FALSE,
    acknowledged_by UUID REFERENCES users(id) ON DELETE SET NULL,
    acknowledged_at TIMESTAMPTZ,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_violations_camera ON violations(camera_id);
CREATE INDEX idx_violations_site ON violations(site_id);
CREATE INDEX idx_violations_type ON violations(violation_type);
CREATE INDEX idx_violations_severity ON violations(severity);
CREATE INDEX idx_violations_created ON violations(created_at DESC);
CREATE INDEX idx_violations_tracking ON violations(tracking_id);
CREATE INDEX idx_violations_frame_ts ON violations(frame_timestamp DESC);

-- ---------------------------------------------------------------------------
-- Alerts — Real-time alert records linked to violations
-- ---------------------------------------------------------------------------
CREATE TABLE alerts (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    violation_id    UUID NOT NULL REFERENCES violations(id) ON DELETE CASCADE,
    camera_id       UUID NOT NULL REFERENCES cameras(id) ON DELETE CASCADE,
    site_id         UUID NOT NULL REFERENCES sites(id) ON DELETE CASCADE,
    title           VARCHAR(255) NOT NULL,
    message         TEXT NOT NULL,
    severity        violation_severity NOT NULL,
    status          alert_status DEFAULT 'pending',
    assigned_to     UUID REFERENCES users(id) ON DELETE SET NULL,
    resolved_by     UUID REFERENCES users(id) ON DELETE SET NULL,
    resolved_at     TIMESTAMPTZ,
    resolution_note TEXT,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_alerts_violation ON alerts(violation_id);
CREATE INDEX idx_alerts_camera ON alerts(camera_id);
CREATE INDEX idx_alerts_site ON alerts(site_id);
CREATE INDEX idx_alerts_status ON alerts(status);
CREATE INDEX idx_alerts_severity ON alerts(severity);
CREATE INDEX idx_alerts_created ON alerts(created_at DESC);

-- ---------------------------------------------------------------------------
-- Recordings — Camera recording segments
-- ---------------------------------------------------------------------------
CREATE TABLE recordings (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    camera_id       UUID NOT NULL REFERENCES cameras(id) ON DELETE CASCADE,
    site_id         UUID NOT NULL REFERENCES sites(id) ON DELETE CASCADE,
    file_url        TEXT,
    file_key        VARCHAR(500),
    file_size_bytes BIGINT,
    duration_seconds INTEGER,
    start_time      TIMESTAMPTZ NOT NULL,
    end_time        TIMESTAMPTZ,
    status          recording_status DEFAULT 'recording',
    metadata        JSONB DEFAULT '{}'::jsonb,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_recordings_camera ON recordings(camera_id);
CREATE INDEX idx_recordings_site ON recordings(site_id);
CREATE INDEX idx_recordings_start ON recordings(start_time DESC);
CREATE INDEX idx_recordings_status ON recordings(status);

-- ---------------------------------------------------------------------------
-- Audit Log — Security and compliance audit trail
-- ---------------------------------------------------------------------------
CREATE TABLE audit_logs (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id         UUID REFERENCES users(id) ON DELETE SET NULL,
    action          VARCHAR(100) NOT NULL,
    resource_type   VARCHAR(100),
    resource_id     UUID,
    details         JSONB DEFAULT '{}'::jsonb,
    ip_address      INET,
    user_agent      TEXT,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_audit_user ON audit_logs(user_id);
CREATE INDEX idx_audit_action ON audit_logs(action);
CREATE INDEX idx_audit_created ON audit_logs(created_at DESC);

-- ---------------------------------------------------------------------------
-- Updated_at trigger function
-- ---------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_sites_updated_at BEFORE UPDATE ON sites
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trg_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trg_cameras_updated_at BEFORE UPDATE ON cameras
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trg_alerts_updated_at BEFORE UPDATE ON alerts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ---------------------------------------------------------------------------
-- Seed: Default site and admin user (password: Admin@123 — change in production)
-- Hash generated with bcrypt rounds=12
-- ---------------------------------------------------------------------------
INSERT INTO sites (id, name, code, description, timezone)
VALUES (
    'a0000000-0000-0000-0000-000000000001',
    'Demo Tower Site',
    'DEMO-001',
    'Default demonstration site for Phase 1 MVP',
    'Asia/Kolkata'
);

INSERT INTO users (id, email, password_hash, full_name, role, site_id)
VALUES (
    'b0000000-0000-0000-0000-000000000001',
    'admin@towerai.local',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.G2oX.Q3K5xK5xu',
    'System Administrator',
    'admin',
    'a0000000-0000-0000-0000-000000000001'
);

INSERT INTO cameras (id, site_id, name, code, rtsp_url, location_label, status)
VALUES (
    'c0000000-0000-0000-0000-000000000001',
    'a0000000-0000-0000-0000-000000000001',
    'Tower Base Camera',
    'CAM-001',
    'rtsp://demo:demo@192.168.1.100:554/stream1',
    'Tower Base — North Side',
    'offline'
);
