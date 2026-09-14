# API additions (Phase 2)

* `POST /chat` — `{message, conversation_id?}`; returns intent, confidence, grounded source
  references, and escalation/lead identifiers.
* `GET /conversations/{conversation_id}/messages` — persisted transcript and metadata.
* `POST /leads`, `GET /leads` — lead details and transparent score reasons.
* `POST /escalations`, `GET /escalations` — human escalation queue.

Phase 1 property and knowledge routes remain available.

## Frontend integration

The Next.js client uses `NEXT_PUBLIC_API_URL` and calls the routes above directly. The API allows
the configured `FRONTEND_URL` origin for browser requests. No frontend-only proxy or altered
response contract is required.
