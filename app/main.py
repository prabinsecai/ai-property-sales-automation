from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func, select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from .config import get_settings
from .db import get_session, init_db
from .embeddings import get_embedding_provider
from .ingestion import ingest
from .models import Property, Conversation, Message, RetrievalTrace, Lead, Escalation
from .schemas import (IngestResponse, KnowledgeSearchRequest, PropertyList, PropertyOut,
                      SearchRequest, SearchResponse, SearchResult, ChatRequest, ChatResponse,
                      LeadCreate, LeadOut, EscalationCreate, EscalationOut, SourceReference)
from .agent import grounded_answer
from .understanding import understand_query
from .search import interpreted_filters, natural_search, structured_search, text_for_property
from .vectorstore import VectorStore

app = FastAPI(title="Phase 1 Property Search API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[get_settings().frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup() -> None:
    await init_db()


def output(p: Property) -> PropertyOut:
    data = {k: getattr(p, k) for k in ("id", "property_id", "title", "description", "city",
            "suburb", "address", "state", "property_type", "price", "weekly_rent", "bedrooms",
            "bathrooms", "parking", "pet_policy", "lease_duration", "image_url", "is_available",
            "availability_status", "available_date", "created_at", "updated_at")}
    data["area_sqft"] = p.area_sqft
    data["year_built"] = p.year_built
    data["amenities"] = [x.strip() for x in p.amenities.split(",") if x.strip()]
    data["nearby_facilities"] = [x.strip() for x in p.nearby_facilities.split(",") if x.strip()]
    return PropertyOut(**data)


@app.get("/health")
async def health() -> dict[str, str]:
    settings = get_settings()
    return {"status": "ok", "service": "property-search-api",
            "environment": settings.embedding_mode}


@app.get("/properties", response_model=PropertyList)
async def properties(page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100),
                     city: str | None = None, suburb: str | None = None, state: str | None = None,
                     property_type: str | None = None, min_price: float | None = Query(None, ge=0),
                     max_price: float | None = Query(None, ge=0),
                     min_bedrooms: int | None = Query(None, ge=0),
                     max_bedrooms: int | None = Query(None, ge=0),
                     bedrooms: int | None = Query(None, ge=0),
                     bathrooms: float | None = Query(None, ge=0),
                     parking_required: bool | None = None, pet_friendly: bool | None = None,
                     availability_status: str | None = None,
                     session: AsyncSession = Depends(get_session)):
    request = SearchRequest(city=city, suburb=suburb, state=state, property_type=property_type,
                            min_price=min_price, max_price=max_price,
                            min_bedrooms=min_bedrooms, max_bedrooms=max_bedrooms,
                            bedrooms=bedrooms, bathrooms=bathrooms,
                            parking_required=parking_required, pet_friendly=pet_friendly,
                            availability_status=availability_status,
                            limit=page * page_size)
    rows, total = await structured_search(session, request.model_copy(update={}))
    rows = rows[(page - 1) * page_size: page * page_size]
    return PropertyList(items=[output(p) for p in rows], total=total, page=page, page_size=page_size)


@app.get("/properties/{property_id}", response_model=PropertyOut)
async def property_detail(property_id: str, session: AsyncSession = Depends(get_session)):
    item = await session.scalar(select(Property).where(Property.property_id == property_id))
    if item is None and property_id.isdigit():
        item = await session.get(Property, int(property_id))
    if not item:
        raise HTTPException(404, "Property not found")
    return output(item)


@app.post("/properties/search", response_model=SearchResponse)
@app.post("/api/v1/search", response_model=SearchResponse, include_in_schema=False)
async def search(request: SearchRequest, session: AsyncSession = Depends(get_session)):
    if request.query:
        ranked, total = await natural_search(session, request)
        return SearchResponse(
            results=[SearchResult(property=output(p), score=score, match_type="natural")
                     for p, score in ranked],
        total=total, query=request.query, interpreted_filters=interpreted_filters(request))
    rows, total = await structured_search(session, request)
    return SearchResponse(results=[SearchResult(property=output(p), score=1.0, match_type="structured")
                                   for p in rows], total=total, query=request.query)


@app.post("/knowledge/reindex", response_model=IngestResponse)
async def ingest_endpoint(session: AsyncSession = Depends(get_session)):
    try:
        indexed = await ingest(session)
    except (ImportError, RuntimeError, ValueError) as exc:
        raise HTTPException(503, f"Knowledge reindex unavailable: {exc}") from exc
    return IngestResponse(indexed=indexed, collection=VectorStore.collection_name)


@app.get("/knowledge/search/{property_id}", response_model=list[SearchResult])
async def retrieval(property_id: str, limit: int = Query(10, ge=1, le=50),
                    session: AsyncSession = Depends(get_session)):
    item = await session.scalar(select(Property).where(Property.property_id == property_id))
    if item is None and property_id.isdigit():
        item = await session.get(Property, int(property_id))
    if not item:
        raise HTTPException(404, "Property not found")
    vectors = await get_embedding_provider().embed([text_for_property(item)])
    neighbors = VectorStore(get_settings().chroma_path).query(vectors[0], limit + 1)
    ids = [n["id"] for n in neighbors if n["id"] != item.property_id][:limit]
    rows = (await session.scalars(select(Property).where(Property.property_id.in_(ids)))).all()
    scores = {n["id"]: n["score"] for n in neighbors}
    return [SearchResult(property=output(p), score=scores.get(p.property_id, 0), match_type="vector")
            for p in rows]


@app.post("/properties/search/natural", response_model=SearchResponse)
async def natural(request: SearchRequest, session: AsyncSession = Depends(get_session)):
    ranked, total = await natural_search(session, request)
    return SearchResponse(results=[SearchResult(property=output(p), score=score, match_type="natural")
                                   for p, score in ranked], total=total, query=request.query,
                          interpreted_filters=interpreted_filters(request))


@app.post("/knowledge/search")
async def knowledge_search(request: KnowledgeSearchRequest, session: AsyncSession = Depends(get_session)):
    try:
        provider = get_embedding_provider()
        store = VectorStore(get_settings().chroma_path)
    except (ImportError, RuntimeError, ValueError) as exc:
        raise HTTPException(503, f"Knowledge search unavailable: {exc}") from exc
    if store.count() == 0:
        raise HTTPException(409, "Knowledge index is empty; run POST /knowledge/reindex first")
    try:
        vectors = await provider.embed([request.query])
        matches = store.query(vectors[0], request.limit)
    except (RuntimeError, ValueError) as exc:
        raise HTTPException(503, f"Knowledge search failed: {exc}") from exc
    ids = [match["metadata"].get("property_id", match["id"]) for match in matches]
    rows = (await session.scalars(select(Property).where(Property.property_id.in_(ids)))).all()
    by_id = {p.property_id: p for p in rows}
    return {"query": request.query, "results": [
        {"property": output(by_id[pid]), "score": match["score"], "match_type": "vector",
         "metadata": match["metadata"], "document": match["document"]}
        for pid, match in zip(ids, matches) if pid in by_id
    ]}


def lead_score(data: LeadCreate) -> tuple[float, list[str]]:
    reasons = []
    score = 0.0
    if data.email:
        score += 35; reasons.append("email provided")
    if data.phone:
        score += 20; reasons.append("phone provided")
    if data.budget is not None:
        score += 25; reasons.append("budget provided")
    if data.intent:
        score += 20; reasons.append("intent provided")
    return min(score, 100), reasons


def lead_out(item: Lead) -> LeadOut:
    return LeadOut.model_validate(item, from_attributes=True)


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, session: AsyncSession = Depends(get_session)):
    conversation_id = request.conversation_id or __import__("uuid").uuid4().hex
    conversation = await session.scalar(select(Conversation).where(
        Conversation.conversation_id == conversation_id))
    if not conversation:
        conversation = Conversation(conversation_id=conversation_id)
        session.add(conversation)
    history_rows = (await session.scalars(select(Message).where(
        Message.conversation_id == conversation_id).order_by(desc(Message.created_at)).limit(10))).all()
    history = [{"role": row.role, "content": row.content} for row in reversed(history_rows)]
    session.add(Message(conversation_id=conversation_id, role="user", content=request.message))
    try:
        answer, grounded, understanding, refs = await grounded_answer(
            session, request.message, history)
    except RuntimeError as exc:
        await session.rollback()
        raise HTTPException(503, f"LLM provider unavailable: {exc}") from exc
    session.add(Message(conversation_id=conversation_id, role="assistant", content=answer,
                        intent=understanding.intent, confidence=understanding.confidence,
                        source_references=refs))
    session.add(RetrievalTrace(conversation_id=conversation_id, query=request.message,
                               references=refs))
    escalation_id = None
    if understanding.unsupported or understanding.confidence < 0.6:
        escalation = Escalation(conversation_id=conversation_id,
                                reason="unsupported_request" if understanding.unsupported else "low_confidence",
                                message=request.message)
        session.add(escalation)
        await session.flush()
        escalation_id = escalation.id
    # Extract and upsert a lead whenever contact or qualification data is present.
    entity = understanding.entities
    lead_id = None
    if entity:
        lead_data = LeadCreate(conversation_id=conversation_id, name=entity.get("name"),
                               email=entity.get("email"),
                               phone=entity.get("phone"), budget=entity.get("budget"),
                               intent=understanding.intent)
        lead = await session.scalar(select(Lead).where(Lead.conversation_id == conversation_id))
        if not lead:
            lead = Lead(conversation_id=conversation_id)
            session.add(lead)
        for key, value in lead_data.model_dump(exclude_unset=True).items():
            if key != "conversation_id" and value is not None:
                setattr(lead, key, value)
        merged = LeadCreate(conversation_id=conversation_id, name=lead.name, email=lead.email,
                            phone=lead.phone, intent=lead.intent, budget=lead.budget,
                            preferences=lead.preferences or {})
        lead.score, lead.score_reasons = lead_score(merged)
        await session.flush()
        lead_id = lead.id
    await session.commit()
    return ChatResponse(conversation_id=conversation_id, message=answer, intent=understanding.intent,
                        confidence=understanding.confidence,
                        source_references=[SourceReference(**r) for r in refs],
                        escalated=escalation_id is not None, escalation_id=escalation_id,
                        lead_id=lead_id, property_ids=[r["source_id"] for r in refs],
                        sources=[SourceReference(**r) for r in refs],
                        lead_detected=lead_id is not None,
                        escalation_required=escalation_id is not None)


@app.get("/conversations/{conversation_id}/messages")
async def conversation_messages(conversation_id: str, session: AsyncSession = Depends(get_session)):
    rows = (await session.scalars(select(Message).where(
        Message.conversation_id == conversation_id).order_by(Message.created_at))).all()
    return [{"role": row.role, "content": row.content, "intent": row.intent,
             "confidence": row.confidence, "source_references": row.source_references or []}
            for row in rows]


@app.post("/leads", response_model=LeadOut)
async def create_lead(data: LeadCreate, session: AsyncSession = Depends(get_session)):
    score, reasons = lead_score(data)
    item = None
    if data.conversation_id:
        item = await session.scalar(select(Lead).where(Lead.conversation_id == data.conversation_id))
    if item is None:
        item = Lead(**data.model_dump())
        session.add(item)
    else:
        for key, value in data.model_dump(exclude_unset=True).items():
            if value is not None:
                setattr(item, key, value)
    merged = LeadCreate(conversation_id=item.conversation_id, name=item.name, email=item.email,
                        phone=item.phone, intent=item.intent, budget=item.budget,
                        preferences=item.preferences or {})
    item.score, item.score_reasons = lead_score(merged)
    await session.commit()
    await session.refresh(item)
    return lead_out(item)


@app.get("/leads/{lead_id}", response_model=LeadOut)
async def get_lead(lead_id: int, session: AsyncSession = Depends(get_session)):
    item = await session.get(Lead, lead_id)
    if item is None:
        raise HTTPException(404, "Lead not found")
    return lead_out(item)


@app.get("/leads", response_model=list[LeadOut])
async def list_leads(page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100),
                     minimum_score: float | None = Query(None, ge=0, le=100),
                     session: AsyncSession = Depends(get_session)):
    stmt = select(Lead)
    if minimum_score is not None:
        stmt = stmt.where(Lead.score >= minimum_score)
    rows = (await session.scalars(stmt.order_by(desc(Lead.created_at)).offset(
        (page - 1) * page_size).limit(page_size))).all()
    return [lead_out(x) for x in rows]


@app.post("/escalations", response_model=EscalationOut)
async def create_escalation(data: EscalationCreate, session: AsyncSession = Depends(get_session)):
    item = Escalation(**data.model_dump())
    session.add(item)
    await session.commit()
    await session.refresh(item)
    return item


@app.get("/escalations/{escalation_id}", response_model=EscalationOut)
async def get_escalation(escalation_id: int, session: AsyncSession = Depends(get_session)):
    item = await session.get(Escalation, escalation_id)
    if item is None:
        raise HTTPException(404, "Escalation not found")
    return item


@app.get("/escalations", response_model=list[EscalationOut])
async def list_escalations(page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100),
                           status: str | None = None,
                           session: AsyncSession = Depends(get_session)):
    stmt = select(Escalation)
    if status:
        stmt = stmt.where(Escalation.status == status)
    return (await session.scalars(stmt.order_by(desc(Escalation.created_at)).offset(
        (page - 1) * page_size).limit(page_size))).all()
