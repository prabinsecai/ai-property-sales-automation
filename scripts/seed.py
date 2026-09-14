import asyncio
from datetime import date
from app.db import SessionLocal, init_db
from app.models import Property
from sqlalchemy import select


async def main() -> None:
    await init_db()
    async with SessionLocal() as session:
        cities = [("Austin", "Texas"), ("Denver", "Colorado"), ("Portland", "Oregon"),
                  ("Miami", "Florida"), ("Raleigh", "North Carolina"), ("Seattle", "Washington"),
                  ("Sydney", "NSW")]
        kinds = ["house", "apartment", "condo", "townhouse", "villa"]
        for i in range(36):
            city, state = cities[i % len(cities)]
            kind = kinds[i % len(kinds)]
            property_id = f"PROP-{i + 1:03d}"
            if await session.scalar(select(Property.id).where(Property.property_id == property_id)):
                continue
            session.add(Property(title=f"{city} {kind.title()} {i + 1}",
                property_id=property_id,
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
        sydney_properties = [
            {
                "property_id": "SYD-101",
                "title": "Harbour View Apartment",
                "suburb": "Surry Hills",
                "address": "101 Crown Street",
                "weekly_rent": 650,
                "bedrooms": 2,
                "bathrooms": 1,
                "parking": 1,
                "description": "Bright apartment near transit, parks, and local dining.",
            },
            {
                "property_id": "SYD-102",
                "title": "Redfern Park Apartment",
                "suburb": "Redfern",
                "address": "22 Regent Street",
                "weekly_rent": 720,
                "bedrooms": 2,
                "bathrooms": 2,
                "parking": 1,
                "description": "Modern apartment with a balcony close to Redfern Station.",
            },
        ]
        for index, item in enumerate(sydney_properties, start=1):
            if await session.scalar(select(Property.id).where(
                    Property.property_id == item["property_id"])):
                continue
            session.add(Property(
                **item,
                city="Sydney",
                state="NSW",
                property_type="apartment",
                price=700000 + index * 25000,
                area_sqft=850 + index * 50,
                year_built=2020 + index,
                amenities="balcony, gym, secure entry",
                nearby_facilities="transit, parks, shops",
                pet_policy="allowed",
                lease_duration="12 months",
                availability_status="available",
                available_date=date(2026, 10, 1),
                image_url=None,
            ))
        await session.commit()


if __name__ == "__main__":
    asyncio.run(main())
