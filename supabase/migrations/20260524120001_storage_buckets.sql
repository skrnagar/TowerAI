-- Tower AI — Supabase Storage buckets (violation screenshots, recordings)

INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
VALUES
  (
    'violation-screenshots',
    'violation-screenshots',
    false,
    52428800,
    ARRAY['image/jpeg', 'image/png', 'image/webp']::text[]
  ),
  (
    'recordings',
    'recordings',
    false,
    524288000,
    ARRAY['video/mp4', 'video/webm', 'video/quicktime']::text[]
  )
ON CONFLICT (id) DO UPDATE SET
  file_size_limit = EXCLUDED.file_size_limit,
  allowed_mime_types = EXCLUDED.allowed_mime_types;

-- Authenticated users: read violation screenshots
CREATE POLICY "towerai_violation_screenshots_select"
ON storage.objects FOR SELECT
TO authenticated
USING (bucket_id = 'violation-screenshots');

-- Service role: full access to both buckets (backend / edge functions)
CREATE POLICY "towerai_storage_service_role_all"
ON storage.objects FOR ALL
TO service_role
USING (bucket_id IN ('violation-screenshots', 'recordings'))
WITH CHECK (bucket_id IN ('violation-screenshots', 'recordings'));
