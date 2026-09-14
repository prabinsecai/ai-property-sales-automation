from datetime import date, datetime
from pydantic import BaseModel, ConfigDict, Field, field_validator
import re


class PropertyOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    property_id: str
    title: str
    description: str
    city: str
    suburb: str
    address: str
    state: str
    property_type: str
    price: float
    weekly_rent: float
    bedrooms: int
    bathrooms: float
    parking: int
    pet_policy: str
    lease_duration: str
    nearby_facilities: list[str]
    area_sqft: int
    year_built: int
    amenities: list[str]
    image_url: str | None
    is_available: bool
    availability_status: str
    available_date: date | None
    created_at: datetime
    updated_at: datetime


class PropertyList(BaseModel):
    items: list[PropertyOut]
    total: int
    page: int
    page_size: int


class SearchRequest(BaseModel):
    query: str | None = Field(default=None, max_length=1000)
    city: str | None = None
    suburb: str | None = None
    state: str | None = None
    property_type: str | None = None
    min_price: float | None = Field(default=None, ge=0)
    max_price: float | None = Field(default=None, ge=0)
    min_bedrooms: int | None = Field(default=None, ge=0)
    max_bedrooms: int | None = Field(default=None, ge=0)
    bedrooms: int | None = Field(default=None, ge=0)
    min_bathrooms: float | None = Field(default=None, ge=0)
    bathrooms: float | None = Field(default=None, ge=0)
    parking: int | None = Field(default=None, ge=0)
    parking_required: bool | None = None
    pet_policy: str | None = None
    pet_friendly: bool | None = None
    availability_status: str | None = None
    limit: int = Field(default=10, ge=1, le=50)


class SearchResult(BaseModel):
    property: PropertyOut
    score: float
    match_type: str


class SearchResponse(BaseModel):
    results: list[SearchResult]
    total: int
    query: str | None
    interpreted_filters: dict[str, object] = {}


class IngestResponse(BaseModel):
    indexed: int
    collection: str


class KnowledgeSearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=1000)
    limit: int = Field(default=10, ge=1, le=50)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    conversation_id: str | None = None


class SourceReference(BaseModel):
    source_type: str
    source_id: str
    title: str | None = None
    excerpt: str | None = None


class ChatResponse(BaseModel):
    conversation_id: str
    message: str
    intent: str
    confidence: float
    source_references: list[SourceReference] = []
    escalated: bool = False
    escalation_id: int | None = None
    lead_id: int | None = None
    property_ids: list[str] = []
    sources: list[SourceReference] = []
    lead_detected: bool = False
    escalation_required: bool = False


class LeadCreate(BaseModel):
    conversation_id: str | None = None
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    intent: str | None = None
    budget: float | None = None
    preferences: dict[str, object] | None = None

    @field_validator("email")
    @classmethod
    def valid_email(cls, value):
        if value is not None and not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", value):
            raise ValueError("email must be a valid email address")
        return value

    @field_validator("phone")
    @classmethod
    def valid_phone(cls, value):
        if value is not None and not re.fullmatch(r"\+?[0-9 ()-]{8,20}", value):
            raise ValueError("phone must contain 8-20 digits and may include +, spaces, or -")
        return value


class LeadOut(LeadCreate):
    id: int
    score: float
    score_reasons: list[str] = []
    created_at: datetime
    updated_at: datetime


class EscalationCreate(BaseModel):
    conversation_id: str
    reason: str
    message: str


class EscalationOut(EscalationCreate):
    id: int
    status: str
    created_at: datetime
