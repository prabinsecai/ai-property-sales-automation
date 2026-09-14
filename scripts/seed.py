import asyncio
from datetime import date
from app.db import SessionLocal, init_db
from app.models import Property


async def main() -> None:
    await init_db()
    async with SessionLocal() as session:
        if await session.scalar(__import__("sqlalchemy").select(Property.id).limit(1)):
            return
        cities = [("Austin", "Texas"), ("Denver", "Colorado"), ("Portland", "Oregon"),
                  ("Miami", "Florida"), ("Raleigh", "North Carolina"), ("Seattle", "Washington")]
        kinds = ["house", "apartment", "condo", "townhouse", "villa"]
        for i in range(36):
            city, state = cities[i % len(cities)]
            kind = kinds[i % len(kinds)]
            session.add(Property(title=f"{city} {kind.title()} {i + 1}",
                property_id=f"PROP-{i + 1:03d}",
                description=f"Bright fictional {kind} near parks and local dining.",
                city=city, suburb=f"{city} Heights", address=f"{100+i} Market Street",
                state=state, property_type=kind, price=180000 + i * 27500,
                weekly_rent=450 + i * 20,
                bedrooms=1 + i % 5, bathrooms=1 + (i % 3) * 0.5, area_sqft=700 + i * 55,
                year_built=1990 + i % 35, amenities="parking, gym, patio" if i % 2 else "garden, pool",
                parking=i % 3, pet_policy="allowed" if i % 2 else "no pets",
                lease_duration="12 months", nearby_facilities="school, transit, shops",
                availability_status="available", available_date=date(2026, 10, 1),
                image_url=f"https://example.com/properties/{i + 1}.jpg"))
        await session.commit()


if __name__ == "__main__":
    asyncio.run(main())
