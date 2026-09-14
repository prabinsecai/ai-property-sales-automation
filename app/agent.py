from sqlalchemy.ext.asyncio import AsyncSession
from .search import natural_search, structured_search
from .schemas import SearchRequest
from .understanding import QueryUnderstanding, understand_query
from .validation import validate_response


async def grounded_answer(
    session: AsyncSession, text: str, history: list[dict[str, str]] | None = None
) -> tuple[str, bool, QueryUnderstanding, list[dict]]:
    prior = {}
    if history:
        for item in history[-10:]:
            prior.update(understand_query(item["content"]).entities)
    understanding = understand_query(text, prior)
    if understanding.unsupported:
        return ("I can't make guarantees or provide legal advice. I'll connect you with a human "
                "specialist to help.", False, understanding, [])
    filters = {k: v for k, v in understanding.entities.items()
               if k in {"city", "property_type", "bedrooms", "parking_required"}}
    if "budget" in understanding.entities:
        filters["max_price"] = understanding.entities["budget"]
    request = SearchRequest(query=text, limit=5, **filters)
    if filters:
        rows, _ = await structured_search(session, request)
        ranked = [(p, 1.0) for p in rows]
    else:
        ranked, _ = await natural_search(session, request)
    refs = [{
        "source_type": "property",
        "source_id": p.property_id,
        "title": p.title,
        "excerpt": (
            f"Location: {p.suburb}, {p.city}, {p.state}. "
            f"{p.bedrooms} bedrooms. Weekly rent: ${p.weekly_rent:,.0f}."
        ),
    } for p, _ in ranked[:3]]
    if not refs:
        return ("I couldn't find any available properties matching those requirements.",
                True, understanding, [])
    lines = ["Here are available properties matching your request:"]
    for ref in refs:
        lines.append(f"- {ref['title']} — {ref['excerpt']} Source: {ref['source_id']}.")
    response = "\n".join(lines)
    context = " ".join(f"{r['title']} ({r['source_id']}): {r['excerpt']}" for r in refs)
    return (*validate_response(response, context), understanding, refs)
