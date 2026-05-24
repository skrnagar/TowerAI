#!/usr/bin/env bash
# Sync Tower AI Supabase remote: migrations, types, edge functions
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

echo "==> Project link"
supabase projects list | grep -q edwdhyoghxnqrgzrocol || supabase link --project-ref edwdhyoghxnqrgzrocol

echo "==> Mark baseline migration applied (schema already on remote)"
supabase migration repair 20260524120000 --status applied 2>/dev/null || true

echo "==> Push migrations (storage, RLS, realtime)"
supabase db push

echo "==> Generate TypeScript types"
mkdir -p frontend/src/types
supabase gen types typescript --linked > frontend/src/types/supabase.ts

echo "==> Deploy edge functions"
supabase functions deploy health --no-verify-jwt
supabase functions deploy violation-webhook --no-verify-jwt

echo "==> Done. Set SUPABASE_SERVICE_ROLE_KEY in backend/.env (from: supabase projects api-keys)"
