import pytest
from app.embeddings import DeterministicEmbedding, get_embedding_provider
from app.models import Property
from app.schemas import SearchRequest
from app.search import interpreted_filters, parse_natural_query, text_for_property
from app.config import get_settings
from app.vectorstore import VectorStore


@pytest.mark.asyncio
async def test_deterministic_embedding_is_stable():
    provider = DeterministicEmbedding()
    assert await provider.embed(["hello"]) == await provider.embed(["hello"])
    assert len((await provider.embed(["hello"]))[0]) == 64


def test_natural_query_interprets_parking_pets_and_bedrooms():
    request = SearchRequest(query="3 bedroom pet friendly home with parking under $700")
    parsed = parse_natural_query(request)
    assert parsed.min_bedrooms == 3
    assert parsed.parking_required is True
    assert parsed.pet_friendly is True
    assert interpreted_filters(request)["parking_required"] is True


def test_document_builder_contains_metadata_fields():
    item = Property(property_id="P-1", title="Test", description="Quiet home",
                    city="Austin", suburb="Central", address="1 Main", state="TX",
                    property_type="house", price=1, weekly_rent=700, bedrooms=3,
                    bathrooms=2, area_sqft=1, year_built=2020, amenities="garden",
                    nearby_facilities="school", pet_policy="allowed")
    document = text_for_property(item)
    assert "Austin" in document and "school" in document and "allowed" in document


def test_openai_mode_requires_configuration(monkeypatch):
    monkeypatch.setenv("EMBEDDING_MODE", "openai")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    get_settings.cache_clear()
    with pytest.raises(RuntimeError):
        get_embedding_provider()


def test_vector_query_preserves_ids_and_metadata():
    class Collection:
        def query(self, **kwargs):
            return {"ids": [["PROP-001"]], "distances": [[0.1]],
                    "documents": [["document"]], "metadatas": [{"property_id": "PROP-001"}]}
    store = object.__new__(VectorStore)
    store.collection = Collection()
    result = store.query([0.0, 1.0], 1)
    assert result[0]["id"] == "PROP-001"
    assert result[0]["metadata"]["property_id"] == "PROP-001"
