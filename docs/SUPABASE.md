# Supabase Integration

Project ref: `edwdhyoghxnqrgzrocol`  
Dashboard: https://supabase.com/dashboard/project/edwdhyoghxnqrgzrocol

---

## Frontend (Next.js)

Packages: `@supabase/supabase-js`, `@supabase/ssr`

| File | Purpose |
|------|---------|
| `frontend/src/utils/supabase/client.ts` | Browser client |
| `frontend/src/utils/supabase/server.ts` | Server Components / Route Handlers |
| `frontend/src/utils/supabase/middleware.ts` | Session refresh |
| `frontend/src/middleware.ts` | Applies session refresh on each request |
| `frontend/src/app/auth/callback/route.ts` | OAuth / magic-link callback |
| `frontend/.env.local` | Local keys (gitignored) |

### Environment variables

```bash
cp frontend/.env.local.example frontend/.env.local
```

Required:

- `NEXT_PUBLIC_SUPABASE_URL`
- `NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY`

### Usage in Server Components

```tsx
import { createClient } from "@/utils/supabase/server";

export default async function Page() {
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  const { data: rows } = await supabase.from("your_table").select();
  // ...
}
```

### Usage in Client Components

```tsx
"use client";
import { createClient } from "@/utils/supabase/client";

const supabase = createClient();
```

---

## Supabase CLI

Install (macOS):

```bash
brew install supabase/tap/supabase
```

Then from repo root:

```bash
supabase login
supabase link --project-ref edwdhyoghxnqrgzrocol
```

`supabase init` is already done — config lives in `supabase/config.toml`.

Pull remote schema:

```bash
supabase db pull
```

Push local migrations:

```bash
supabase db push
```

---

## Backend (FastAPI) — PostgreSQL

Use the **Session pooler** connection string if your network is IPv4-only.

Direct (IPv6):

```
postgresql://postgres:[YOUR-PASSWORD]@db.edwdhyoghxnqrgzrocol.supabase.co:5432/postgres
```

Async SQLAlchemy (backend):

```
DATABASE_URL=postgresql+asyncpg://postgres.[YOUR-PASSWORD]@aws-0-[region].pooler.supabase.com:6543/postgres
```

Set in root `.env` and restart `backend` service.

---

## MCP (Cursor)

Configured in `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "supabase": {
      "url": "https://mcp.supabase.com/mcp?project_ref=edwdhyoghxnqrgzrocol"
    }
  }
}
```

Reload Cursor after editing MCP config.

---

## Optional: Agent Skills

```bash
npx skills add supabase/agent-skills
```

---

## Auth strategy

- **Phase 1 MVP:** FastAPI JWT (`/api/v1/auth/login`) for API access  
- **Supabase Auth:** Use for Next.js session, RLS-backed reads, and future user management  

Both can run in parallel until you migrate users to `auth.users` in Supabase.
