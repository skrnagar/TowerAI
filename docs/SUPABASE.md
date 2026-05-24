# Supabase Integration

**Project:** `edwdhyoghxnqrgzrocol` (SonilAi)  
**Region:** Northeast Asia (Tokyo) — pooler `aws-1-ap-northeast-1`  
**Dashboard:** https://supabase.com/dashboard/project/edwdhyoghxnqrgzrocol

---

## What is configured (CLI)

| Feature | Status | Location |
|---------|--------|----------|
| **Database** | Schema on remote + migration history | `supabase/migrations/`, `infrastructure/postgres/init.sql` |
| **Storage** | Buckets `violation-screenshots`, `recordings` | Migration `20260524120001_storage_buckets.sql` |
| **Auth** | Email signup, localhost redirects | `supabase/config.toml` |
| **RLS + Realtime** | SELECT for `authenticated`; full access for `service_role` | Migration `20260524120002_rls_and_realtime.sql` |
| **Edge Functions** | `health`, `violation-webhook` | `supabase/functions/` |
| **TypeScript types** | Generated from remote schema | `frontend/src/types/supabase.ts` |

---

## One-command sync

From repo root (after `supabase login`):

```bash
make supabase-sync
# or
./scripts/supabase/sync.sh
```

This will:

1. Mark baseline migration as applied (schema already exists)
2. `supabase db push` — apply new migrations
3. Regenerate `frontend/src/types/supabase.ts`
4. Deploy edge functions

Individual targets: `make supabase-push`, `make supabase-types`, `make supabase-functions`

---

## Environment variables

### Frontend (`frontend/.env.local`)

```bash
NEXT_PUBLIC_SUPABASE_URL=https://edwdhyoghxnqrgzrocol.supabase.co
NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY=sb_publishable_...
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Backend (`backend/.env`)

```bash
SUPABASE_URL=https://edwdhyoghxnqrgzrocol.supabase.co
SUPABASE_PUBLISHABLE_KEY=sb_publishable_...
SUPABASE_SERVICE_ROLE_KEY=          # supabase projects api-keys (never commit)
DATABASE_URL=postgresql+asyncpg://postgres.edwdhyoghxnqrgzrocol:PASSWORD@aws-1-ap-northeast-1.pooler.supabase.com:6543/postgres
SUPABASE_VIOLATION_WEBHOOK_URL=https://edwdhyoghxnqrgzrocol.supabase.co/functions/v1/violation-webhook
```

Get keys:

```bash
supabase projects api-keys --project-ref edwdhyoghxnqrgzrocol
```

---

## Database

- **Canonical SQL:** `infrastructure/postgres/init.sql`
- **Migrations:** `supabase/migrations/`
- **Tables:** `sites`, `users`, `cameras`, `violations`, `alerts`, `recordings`, `audit_logs`
- **Seed admin:** `admin@towerai.local` / `Admin@123` (FastAPI JWT; not Supabase Auth yet)

Connection pooler (Session, port 6543 for transaction mode):

```
postgresql+asyncpg://postgres.edwdhyoghxnqrgzrocol:[PASSWORD]@aws-1-ap-northeast-1.pooler.supabase.com:6543/postgres
```

Inspect remote:

```bash
supabase inspect db table-stats --linked
supabase migration list
```

---

## Storage

| Bucket | Purpose | Max size |
|--------|---------|----------|
| `violation-screenshots` | AI / alert frame captures | 50 MiB |
| `recordings` | Camera segment archives | 500 MiB |

**Backend upload** (service role): `backend/app/integrations/supabase_storage.py`  
**Frontend signed URLs:** `frontend/src/lib/supabase-storage.ts`

---

## Auth strategy (dual)

| Layer | Use |
|-------|-----|
| **FastAPI JWT** | Phase 1 API: `/api/v1/auth/login` with `public.users` |
| **Supabase Auth** | Next.js session, OAuth callback, RLS-backed reads |

Enable Supabase Auth users in Dashboard when ready; map `auth.users.id` → `public.users` in a future migration.

---

## Edge functions

### `health`

```bash
curl https://edwdhyoghxnqrgzrocol.supabase.co/functions/v1/health
```

### `violation-webhook`

POST JSON from AI engine (uses service role server-side):

```json
{
  "camera_id": "uuid",
  "site_id": "uuid",
  "violation_type": "helmet_off",
  "severity": "high",
  "confidence": 0.92,
  "frame_timestamp": "2026-05-25T12:00:00Z",
  "bounding_boxes": [],
  "screenshot_key": "optional/path.jpg"
}
```

Deploy:

```bash
supabase functions deploy violation-webhook --no-verify-jwt
```

---

## Realtime (dashboard)

Tables in publication `supabase_realtime`: `violations`, `alerts`, `cameras`.

```tsx
const supabase = createClient();
supabase
  .channel("violations")
  .on("postgres_changes", { event: "INSERT", schema: "public", table: "violations" }, (p) => {
    console.log(p.new);
  })
  .subscribe();
```

---

## MCP (Cursor)

`.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "supabase": {
      "url": "https://mcp.supabase.com/mcp?project_ref=edwdhyoghxnqrgzrocol"
    }
  }
}
```

---

## Local dev (optional)

Requires Docker Desktop:

```bash
supabase start
supabase status
```

Without Docker, use **linked remote** only (`--linked` flags) as this project does.
