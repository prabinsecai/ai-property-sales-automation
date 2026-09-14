# Property Search and Sales Agent API

FastAPI backend and Next.js frontend for fictional property data, structured filters,
natural-language search, embeddings, Chroma-backed retrieval, and a grounded sales agent.

## Run

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
copy .env.example .env
python scripts\seed_database.py
uvicorn app.main:app --reload
```

Open `/docs` for the interactive API documentation.

## Frontend (Phase 3)

```powershell
cd frontend
npm install
copy .env.example .env.local
npm run dev
```

The frontend expects the API at `NEXT_PUBLIC_API_URL` (default `http://localhost:8000`).
It includes property discovery/detail, grounded AI chat, and lead/escalation workspace views.

## Endpoints

- `GET /health`
- `GET /properties` — structured filters and pagination
- `GET /properties/{property_id}`
- `POST /properties/search` — structured search
- `POST /properties/search/natural` — rule-based natural-language search
- `POST /knowledge/reindex` — index database records into Chroma
- `POST /knowledge/search` — retrieve grounded property documents
- `POST /chat` — grounded conversation (mock provider by default)
- `GET /conversations/{conversation_id}/messages`
- `POST/GET /leads`
- `POST/GET /escalations`

Use `python scripts\reindex_knowledge.py` to reindex from the command line. Chroma requires
the native build prerequisites documented in `docs/DEVELOPMENT.md`.

Set `EMBEDDING_MODE=openai` for embeddings and `LLM_MODE=openai` or `anthropic` for generation.
The default `LLM_MODE=mock` is reproducible without network access.
