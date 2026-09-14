"""Canonical knowledge reindex command."""
import asyncio
from app.db import SessionLocal, init_db
from app.ingestion import ingest


async def main() -> None:
    await init_db()
    async with SessionLocal() as session:
        print(f"Indexed {await ingest(session)} properties")


if __name__ == "__main__":
    asyncio.run(main())
