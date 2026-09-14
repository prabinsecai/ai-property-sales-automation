import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete
from app.db import SessionLocal, init_db
from app.main import app
from app.models import (Conversation, Escalation, Lead, Message, Property,
                        RetrievalTrace)
from app.understanding import understand_query


@pytest.fixture
async def client():
    await init_db()
    async with SessionLocal() as session:
        for model in (RetrievalTrace, Message, Conversation, Lead, Escalation, Property):
            await session.execute(delete(model))
        session.add(Property(property_id="P2-1", title="Austin home", description="Sunny",
                             city="Austin", suburb="Central", address="1 Main", state="TX",
                             property_type="house", price=250000, weekly_rent=500, bedrooms=3,
                             bathrooms=2, area_sqft=1200, year_built=2020, amenities="parking",
                             nearby_facilities="school", parking=1, pet_policy="allowed"))
        await session.commit()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as value:
        yield value


@pytest.mark.asyncio
async def test_mock_chat_memory_and_grounding(client):
    first = await client.post("/chat", json={"message": "I need a 3 bedroom house in Austin"})
    assert first.status_code == 200
    conversation_id = first.json()["conversation_id"]
    second = await client.post("/chat", json={"conversation_id": conversation_id,
                                               "message": "my budget is 500"})
    assert second.json()["conversation_id"] == conversation_id
    assert (await client.get(f"/conversations/{conversation_id}/messages")).status_code == 200
    assert second.json()["source_references"][0]["source_id"] == "P2-1"


def test_budget_does_not_capture_bedroom_number():
    parsed = understand_query("2 bedroom apartment under $700")
    assert parsed.entities["bedrooms"] == 2
    assert parsed.entities["budget"] == 700
    assert parsed.intent == "property_search"


@pytest.mark.asyncio
async def test_lead_upsert_validation_and_filters(client):
    response = await client.post("/leads", json={"conversation_id": "c1",
                                                  "email": "buyer@example.com", "budget": 500})
    assert response.status_code == 200
    assert (await client.post("/leads", json={"conversation_id": "c1", "phone": "123"})).status_code == 422
    assert (await client.get("/leads/99999")).status_code == 404
    assert (await client.get("/leads", params={"minimum_score": 50})).json()


@pytest.mark.asyncio
async def test_guarantee_escalates_and_is_retrievable(client):
    response = await client.post("/chat", json={"message": "Can you guarantee this rent?"})
    body = response.json()
    assert body["escalated"] is True
    assert (await client.get(f"/escalations/{body['escalation_id']}")).status_code == 200


@pytest.mark.asyncio
async def test_contact_followup_is_lead_capture_without_escalation(client):
    response = await client.post("/chat", json={
        "message": "My name is John and my email is john@example.com"})
    body = response.json()
    assert body["intent"] == "lead_capture"
    assert body["lead_detected"] is True
    assert body["escalation_required"] is False
    assert body["escalated"] is False


@pytest.mark.asyncio
async def test_sydney_search_filters_and_chat_retrieval(client):
    async with SessionLocal() as session:
        session.add(Property(
            property_id="SYD-1", title="Sydney Harbour Apartment",
            description="Bright apartment near transit", city="Sydney",
            suburb="Surry Hills", address="1 Harbour Road", state="NSW",
            property_type="apartment", price=700000, weekly_rent=650, bedrooms=2,
            bathrooms=1, area_sqft=900, year_built=2020, amenities="balcony",
            nearby_facilities="transit", parking=1, pet_policy="allowed",
        ))
        await session.commit()

    search_response = await client.get("/properties", params={
        "query": "Sydney", "city": "Sydney", "property_type": "Apartment",
        "page_size": 50,
    })
    search_body = search_response.json()
    assert search_body["total"] == 1
    assert search_body["items"][0]["property_id"] == "SYD-1"

    response = await client.post("/chat", json={
        "message": "I'm looking for a 2 bedroom apartment in Sydney "
                   "with a weekly rent under $800. Can you recommend some properties?",
    })
    body = response.json()
    assert body["intent"] == "property_search"
    assert body["source_references"][0]["source_id"] == "SYD-1"
    assert "Sydney Harbour Apartment" in body["message"]
    assert "Surry Hills, Sydney, NSW" in body["message"]
    assert "2 bedrooms" in body["message"]
    assert "$650" in body["message"]


def test_provider_config_and_hallucination_guard(monkeypatch):
    from app.config import get_settings
    from app.llm import get_llm_provider
    from app.validation import validate_response
    monkeypatch.setenv("LLM_MODE", "openai")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    get_settings.cache_clear()
    with pytest.raises(RuntimeError, match="OPENAI_API_KEY"):
        get_llm_provider()
    assert validate_response("Rent is $700", "Weekly rent $500.0")[1] is False
    monkeypatch.setenv("LLM_MODE", "mock")
    get_settings.cache_clear()
