import re
from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from .models import Property
from .schemas import SearchRequest


def text_for_property(p: Property) -> str:
    return f"{p.title}. {p.description} Located at {p.address}, {p.suburb}, {p.city}, {p.state}. " \
           f"{p.property_type}, {p.bedrooms} bedrooms, {p.bathrooms} bathrooms. " \
           f"Amenities: {p.amenities}. Nearby: {p.nearby_facilities}. Pet policy: {p.pet_policy}"


def apply_filters(stmt: Select, request: SearchRequest) -> Select:
    for field, column in (("city", Property.city), ("state", Property.state),
                          ("suburb", Property.suburb), ("property_type", Property.property_type),
                          ("pet_policy", Property.pet_policy), ("availability_status", Property.availability_status)):
        value = getattr(request, field)
        if value:
            stmt = stmt.where(column.ilike(f"%{value}%"))
    if request.parking_required:
        stmt = stmt.where(Property.parking > 0)
    if request.pet_friendly:
        stmt = stmt.where(Property.pet_policy.ilike("%allow%"))
    ranges = (("min_price", Property.weekly_rent, ">="), ("max_price", Property.weekly_rent, "<="),
              ("min_bedrooms", Property.bedrooms, ">="), ("max_bedrooms", Property.bedrooms, "<="),
              ("bedrooms", Property.bedrooms, "="), ("min_bathrooms", Property.bathrooms, ">="), ("bathrooms", Property.bathrooms, "="),
              ("parking", Property.parking, "="))
    for field, column, op in ranges:
        value = getattr(request, field)
        if value is not None:
            stmt = stmt.where(column >= value if op == ">=" else column <= value if op == "<=" else column == value)
    return stmt


def parse_natural_query(request: SearchRequest) -> SearchRequest:
    if not request.query:
        return request
    q = request.query.lower()
    updates = {}
    price = re.search(r"\$?([\d,.]+)\s*(?:k|thousand)?\s*(?:or less|under|max)", q)
    if price:
        value = float(price.group(1).replace(",", ""))
        updates["max_price"] = value * (1000 if "k" in price.group(0) or "thousand" in price.group(0) else 1)
    beds = re.search(r"(\d+)\s*(?:bed|bedroom)", q)
    if beds:
        updates["bedrooms"] = int(beds.group(1))
        updates["min_bedrooms"] = int(beds.group(1))
    for kind in ("house", "apartment", "condo", "townhouse", "villa"):
        if kind in q:
            updates["property_type"] = kind
    if "parking" in q or "garage" in q:
        updates["parking_required"] = True
    if any(term in q for term in ("pet friendly", "pets allowed", "pets welcome")):
        updates["pet_friendly"] = True
    return request.model_copy(update=updates)


def interpreted_filters(request: SearchRequest) -> dict[str, object]:
    parsed = parse_natural_query(request)
    return {k: v for k, v in parsed.model_dump().items()
            if v is not None and k not in ("query", "limit")}


async def structured_search(session: AsyncSession, request: SearchRequest) -> tuple[list[Property], int]:
    request = parse_natural_query(request)
    base = apply_filters(select(Property).where(Property.is_available.is_(True)), request)
    count = await session.scalar(select(func.count()).select_from(base.subquery()))
    rows = (await session.scalars(base.order_by(Property.price).limit(request.limit))).all()
    return rows, int(count or 0)


async def natural_search(session: AsyncSession, request: SearchRequest) -> tuple[list[tuple[Property, float]], int]:
    """Small offline fallback ranker; production retrieval can use the vector endpoint."""
    request = parse_natural_query(request)
    base = apply_filters(select(Property).where(Property.is_available.is_(True)), request.model_copy(update={"query": None}))
    candidates = (await session.scalars(base)).all()
    terms = set(re.findall(r"[a-z0-9]+", (request.query or "").lower()))
    ranked = []
    for item in candidates:
        haystack = set(re.findall(r"[a-z0-9]+", text_for_property(item).lower()))
        score = len(terms & haystack) / max(len(terms), 1)
        ranked.append((item, score))
    ranked.sort(key=lambda pair: (-pair[1], pair[0].price))
    if terms:
        ranked = [pair for pair in ranked if pair[1] > 0]
    return ranked[:request.limit], len(ranked)
