import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app
from app.db import init_db, engine
from app.models import Property
from app.db import SessionLocal
from sqlalchemy import delete


@pytest.fixture(autouse=True)
async def data():
    await init_db()
    async with SessionLocal() as session:
        await session.execute(delete(Property))
        session.add(Property(property_id="TEST-001", title="Test Home", description="A sunny home", city="Austin",
            state="Texas", property_type="house", price=250000, bedrooms=3, bathrooms=2,
            area_sqft=1500, year_built=2020, amenities="garden, parking", suburb="Central",
            address="1 Main St", nearby_facilities="school, transit", parking=1,
            weekly_rent=500, availability_status="available"))
        await session.commit()
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Property.__table__.drop)


@pytest.mark.asyncio
async def test_health_and_structured_search():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        assert (await client.get("/health")).json()["status"] == "ok"
        response = await client.post("/api/v1/search", json={"city": "Austin", "min_bedrooms": 3})
        assert response.status_code == 200
        assert response.json()["total"] == 1
