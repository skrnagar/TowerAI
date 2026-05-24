-- Baseline: Tower AI Phase 1 schema (applied manually via init.sql on remote)
-- See infrastructure/postgres/init.sql for canonical copy.
-- Repaired as applied when remote already has these objects.

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
