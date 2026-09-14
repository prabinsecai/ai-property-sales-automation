from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from .config import get_settings
from .embeddings import get_embedding_provider
from .models import Property
from .search import text_for_property
from .vectorstore import VectorStore


async def ingest(session: AsyncSession) -> int:
    properties = (await session.scalars(select(Property))).all()
    if not properties:
        return 0
    provider = get_embedding_provider()
    texts = [text_for_property(p) for p in properties]
    vectors = await provider.embed(texts)
    store = VectorStore(get_settings().chroma_path)
    store.upsert([p.property_id for p in properties], texts, vectors,
                 [{"property_id": p.property_id, "city": p.city,
                   "suburb": p.suburb, "state": p.state,
                   "property_type": p.property_type} for p in properties])
    return len(properties)
