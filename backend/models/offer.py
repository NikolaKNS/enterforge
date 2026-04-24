"""
Offer (travel proposal) models.
"""

from datetime import datetime, date
from typing import Optional, Dict, Any, List
from uuid import UUID
from enum import Enum
from decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict, field_validator


class OfferStatus(str, Enum):
    """Offer workflow status."""
    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    SENT = "sent"
    CONVERTED = "converted"
    EXPIRED = "expired"


class Meal(BaseModel):
    """Meal recommendation."""
    name: str
    cuisine: str
    price_range: str
    description: Optional[str] = None
    reservation_required: bool = False


class DayPeriod(BaseModel):
    """Activity for a part of the day."""
    activity: str
    location: str
    duration: str
    tip: Optional[str] = None
    cost: Optional[str] = None
    booking_link: Optional[str] = None


class ItineraryDay(BaseModel):
    """Single day in the itinerary."""
    day: int = Field(..., ge=1)
    theme: str
    morning: DayPeriod
    afternoon: DayPeriod
    evening: DayPeriod
    meals: Dict[str, Meal]
    transport: str
    accommodation: Optional[str] = None
    daily_cost: Optional[str] = None
    insider_tip: Optional[str] = None


class FlightSegment(BaseModel):
    """Flight segment details."""
    airline: str
    flight_number: str
    departure_airport: str
    arrival_airport: str
    departure_time: datetime
    arrival_time: datetime
    duration: str
    cabin_class: str
    price: Optional[Decimal] = None


class OfferPricing(BaseModel):
    """Pricing breakdown for an offer."""
    base_cost: Decimal = Field(default=Decimal("0"))
    markup: Decimal = Field(default=Decimal("0"))
    fees: Decimal = Field(default=Decimal("0"))
    taxes: Decimal = Field(default=Decimal("0"))
    total: Decimal = Field(default=Decimal("0"))
    currency: str = "EUR"
    per_person: bool = False
    deposit_required: Optional[Decimal] = None
    payment_terms: Optional[str] = None

    @field_validator('base_cost', 'markup', 'fees', 'taxes', 'total', mode='before')
    @classmethod
    def ensure_decimal(cls, v):
        if v is None:
            return Decimal("0")
        return Decimal(str(v))


class OfferContent(BaseModel):
    """Structured offer content."""
    trip_title: str
    destination: str
    highlights: List[str] = Field(default_factory=list)
    included: List[str] = Field(default_factory=list)
    excluded: List[str] = Field(default_factory=list)
    notes: Optional[str] = None
    terms_and_conditions: Optional[str] = None
    cancellation_policy: Optional[str] = None


class OfferBase(BaseModel):
    """Base offer model."""
    title: str = Field(..., min_length=1, max_length=500)
    destination: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    content_json: OfferContent
    pricing: OfferPricing = Field(default_factory=OfferPricing)
    itinerary: Optional[List[ItineraryDay]] = None
    flights: Optional[List[FlightSegment]] = None


class OfferCreate(BaseModel):
    """Create offer request."""
    agency_id: UUID
    conversation_id: Optional[UUID] = None
    client_id: Optional[UUID] = None
    created_by: UUID
    title: str
    destination: str
    content_json: Dict[str, Any]
    pricing: Dict[str, Any]
    itinerary: Optional[List[Dict[str, Any]]] = None
    flights: Optional[List[Dict[str, Any]]] = None


class OfferUpdate(BaseModel):
    """Update offer request."""
    title: Optional[str] = None
    description: Optional[str] = None
    content_json: Optional[Dict[str, Any]] = None
    pricing: Optional[Dict[str, Any]] = None
    itinerary: Optional[List[Dict[str, Any]]] = None
    flights: Optional[List[Dict[str, Any]]] = None
    valid_until: Optional[date] = None


class Offer(OfferBase):
    """Complete offer model (from database)."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    agency_id: UUID
    conversation_id: Optional[UUID]
    client_id: Optional[UUID]
    created_by: UUID
    status: OfferStatus
    pdf_url: Optional[str] = None
    pdf_generated_at: Optional[datetime] = None

    # Workflow tracking
    submitted_for_approval_at: Optional[datetime] = None
    approved_by: Optional[UUID] = None
    approved_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    sent_at: Optional[datetime] = None
    sent_method: Optional[str] = None

    # Expiration
    valid_until: Optional[date] = None

    created_at: datetime
    updated_at: datetime

    @property
    def is_approved(self) -> bool:
        """Check if offer is approved."""
        return self.status in [OfferStatus.APPROVED, OfferStatus.SENT, OfferStatus.CONVERTED]

    @property
    def can_be_edited(self) -> bool:
        """Check if offer can still be edited."""
        return self.status in [OfferStatus.DRAFT, OfferStatus.REJECTED]

    @property
    def is_expired(self) -> bool:
        """Check if offer has expired."""
        if self.valid_until and self.valid_until < date.today():
            return True
        return False


class OfferWithRelations(Offer):
    """Offer with related data."""
    client: Optional['Client'] = None
    creator: Optional['User'] = None
    approver: Optional['User'] = None
    conversation: Optional['Conversation'] = None


class OfferApprovalRequest(BaseModel):
    """Request to approve an offer."""
    approved_by: UUID
    notes: Optional[str] = None


class OfferRejectionRequest(BaseModel):
    """Request to reject an offer."""
    reason: str = Field(..., min_length=1)


class OfferSendRequest(BaseModel):
    """Request to send offer to client."""
    method: str = Field(default="email", pattern=r"^(email|link|manual)$")
    email_subject: Optional[str] = None
    email_body: Optional[str] = None


# Forward references
from .client import Client
from .user import User
from .conversation import Conversation

OfferWithRelations.model_rebuild()
