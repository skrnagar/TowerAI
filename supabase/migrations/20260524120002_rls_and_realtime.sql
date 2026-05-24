-- Row Level Security + Realtime for dashboard (Supabase client reads)

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_publication_tables
    WHERE pubname = 'supabase_realtime' AND schemaname = 'public' AND tablename = 'violations'
  ) THEN
    ALTER PUBLICATION supabase_realtime ADD TABLE violations;
  END IF;
  IF NOT EXISTS (
    SELECT 1 FROM pg_publication_tables
    WHERE pubname = 'supabase_realtime' AND schemaname = 'public' AND tablename = 'alerts'
  ) THEN
    ALTER PUBLICATION supabase_realtime ADD TABLE alerts;
  END IF;
  IF NOT EXISTS (
    SELECT 1 FROM pg_publication_tables
    WHERE pubname = 'supabase_realtime' AND schemaname = 'public' AND tablename = 'cameras'
  ) THEN
    ALTER PUBLICATION supabase_realtime ADD TABLE cameras;
  END IF;
END $$;

ALTER TABLE sites ENABLE ROW LEVEL SECURITY;
ALTER TABLE cameras ENABLE ROW LEVEL SECURITY;
ALTER TABLE violations ENABLE ROW LEVEL SECURITY;
ALTER TABLE alerts ENABLE ROW LEVEL SECURITY;
ALTER TABLE recordings ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;

-- public.users stays backend-JWT only (no RLS) to avoid conflicting with auth.users

CREATE POLICY "towerai_sites_select_authenticated"
ON sites FOR SELECT TO authenticated USING (true);

CREATE POLICY "towerai_cameras_select_authenticated"
ON cameras FOR SELECT TO authenticated USING (true);

CREATE POLICY "towerai_violations_select_authenticated"
ON violations FOR SELECT TO authenticated USING (true);

CREATE POLICY "towerai_alerts_select_authenticated"
ON alerts FOR SELECT TO authenticated USING (true);

CREATE POLICY "towerai_recordings_select_authenticated"
ON recordings FOR SELECT TO authenticated USING (true);

CREATE POLICY "towerai_audit_logs_select_authenticated"
ON audit_logs FOR SELECT TO authenticated USING (true);

-- Service role (FastAPI with service key, edge functions)
CREATE POLICY "towerai_sites_service_role"
ON sites FOR ALL TO service_role USING (true) WITH CHECK (true);

CREATE POLICY "towerai_cameras_service_role"
ON cameras FOR ALL TO service_role USING (true) WITH CHECK (true);

CREATE POLICY "towerai_violations_service_role"
ON violations FOR ALL TO service_role USING (true) WITH CHECK (true);

CREATE POLICY "towerai_alerts_service_role"
ON alerts FOR ALL TO service_role USING (true) WITH CHECK (true);

CREATE POLICY "towerai_recordings_service_role"
ON recordings FOR ALL TO service_role USING (true) WITH CHECK (true);

CREATE POLICY "towerai_audit_logs_service_role"
ON audit_logs FOR ALL TO service_role USING (true) WITH CHECK (true);
