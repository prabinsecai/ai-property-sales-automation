# HavenFind frontend

This is the Phase 3 Next.js App Router client for the property search and
grounded sales-agent API.

## Development

From this directory:

```powershell
npm install
copy .env.example .env.local
npm run dev
```

Set `NEXT_PUBLIC_API_URL` in `.env.local` when the API is not running at
`http://localhost:8000`.

## Checks

```powershell
npm run lint
npm run typecheck
npm run build
```

The API must be running separately. The client includes property discovery and
detail views, grounded chat, and lead/escalation workspace views.
