# Development

Install with `pip install -e ".[dev]"`, seed 36 records using
`python scripts\seed_database.py`, run `uvicorn app.main:app --reload`, and execute
`python -m pytest -q`. Reindex with `python scripts\reindex_knowledge.py`.
Chroma's native dependency may require Microsoft C++ Build Tools on Windows.
The Phase 3 frontend lives in `frontend/`. Run `npm install`, copy
`frontend\.env.example` to `frontend\.env.local`, and run `npm run dev` from that
directory. The frontend expects the API at `NEXT_PUBLIC_API_URL`.
