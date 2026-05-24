#!/usr/bin/env bash
# Merge root .env into backend/.env (Supabase keys, DATABASE_URL) without overwriting non-placeholder values.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
ROOT_ENV="$ROOT/.env"
BACKEND_ENV="$ROOT/backend/.env"

if [[ ! -f "$BACKEND_ENV" ]]; then
  cp "$ROOT/backend/.env.example" "$BACKEND_ENV"
fi

merge_var() {
  local key="$1"
  local val
  val="$(grep -E "^${key}=" "$ROOT_ENV" 2>/dev/null | head -1 | cut -d= -f2- || true)"
  [[ -z "$val" || "$val" == "YOUR_DB_PASSWORD" ]] && return 0
  if grep -qE "^${key}=" "$BACKEND_ENV"; then
    sed -i.bak "s|^${key}=.*|${key}=${val}|" "$BACKEND_ENV" && rm -f "$BACKEND_ENV.bak"
  else
    echo "${key}=${val}" >> "$BACKEND_ENV"
  fi
}

if [[ -f "$ROOT_ENV" ]]; then
  merge_var "SUPABASE_SERVICE_ROLE_KEY"
  merge_var "DATABASE_URL"
  merge_var "SUPABASE_URL"
  merge_var "SUPABASE_PUBLISHABLE_KEY"
  echo "Synced from $ROOT_ENV -> backend/.env"
else
  echo "No root .env — using backend/.env only"
fi

if grep -q 'YOUR_DB_PASSWORD' "$BACKEND_ENV" 2>/dev/null; then
  echo "WARN: Set DATABASE_URL password in .env or backend/.env (Supabase Dashboard → Database)"
fi
