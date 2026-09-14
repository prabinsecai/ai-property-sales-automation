import re
from dataclasses import dataclass


@dataclass
class QueryUnderstanding:
    intent: str
    confidence: float
    entities: dict[str, object]
    unsupported: bool = False


def understand_query(text: str, prior_entities: dict[str, object] | None = None) -> QueryUnderstanding:
    q = text.lower()
    if any(x in q for x in ("guarantee", "guaranteed", "promise", "legal advice")):
        return QueryUnderstanding("unsupported", 0.99, {}, True)
    if any(x in q for x in ("schedule", "inspection", "viewing", "tour")):
        intent = "inspection"
    elif any(x in q for x in ("buy", "purchase", "property", "home", "house", "apartment")):
        intent = "property_search"
    elif any(x in q for x in ("rent", "price", "cost", "budget")):
        intent = "pricing"
    else:
        intent = "general"
    entities: dict[str, object] = {}
    name = re.search(
        r"\b(?:my name is|i am|i'm)\s+(?!looking\b)([A-Za-z][A-Za-z -]{1,60})",
        text,
        re.I,
    )
    if name:
        entities["name"] = name.group(1).strip(" .,")
    email = re.search(r"[\w.+-]+@[\w.-]+\.\w+", text)
    if email:
        entities["email"] = email.group(0)
    phone = re.search(r"\+?\d[\d ()-]{7,}\d", text)
    if phone:
        entities["phone"] = phone.group(0).strip()
    # Only numbers explicitly associated with money/qualification terms are budgets.
    budget = re.search(
        r"(?:\$\s*([0-9][0-9,]*(?:\.[0-9]+)?)\s*(?:k|thousand)?|"
        r"(?:budget(?:\s*(?:is|of|up to))?|under|below|around|up to|max(?:imum)?)"
        r"\s*:?\s*\$?\s*([0-9][0-9,]*(?:\.[0-9]+)?)\s*(?:k|thousand)?)", q)
    if budget:
        raw_value = budget.group(1) or budget.group(2)
        value = float(raw_value.replace(",", ""))
        if "k" in budget.group(0) or "thousand" in budget.group(0):
            value *= 1000
        entities["budget"] = value
    beds = re.search(r"\b(\d+)\s*(?:bed|bedroom)s?\b", q)
    if beds:
        entities["bedrooms"] = int(beds.group(1))
    for kind in ("house", "apartment", "condo", "townhouse", "villa"):
        if re.search(rf"\b{kind}\b", q):
            entities["property_type"] = kind
    if "parking" in q or "garage" in q:
        entities["parking_required"] = True
    location = re.search(
        r"\b(?:in|near|around)\s+([A-Za-z][A-Za-z'-]*(?:\s+[A-Za-z][A-Za-z'-]*){0,3}?)"
        r"(?=\s+(?:with|and|under|for|near|that|which|please|can)\b|[?.!,]|$)",
        text,
        re.I,
    )
    if location:
        entities["city"] = location.group(1).strip(" .,")
    if prior_entities:
        merged = dict(prior_entities)
        merged.update(entities)
        entities = merged
    if any(key in entities for key in ("name", "email", "phone")):
        intent = "lead_capture"
        confidence = 0.95
    else:
        confidence = 0.8 if intent != "general" else 0.55
    return QueryUnderstanding(intent, confidence, entities)
