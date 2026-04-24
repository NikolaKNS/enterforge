"""
Conversation (AI agent session) models.
"""

from datetime import datetime, date
from typing import Optional, Dict, Any, List
from uuid import UUID
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict


class ConversationStatus(str, Enum):
    """Conversation status values."""
    ACTIVE = "active"
    PENDING_APPROVAL = "pending_approval"
    CLOSED = "closed"
    ARCHIVED = "archived"


class TravelDates(BaseModel):
    """Travel date range."""
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    flexible: bool = False
    duration_days: Optional[int] = None
    preferred_month: Optional[str] = None


class ConversationBase(BaseModel):
    """Base conversation model."""
    title: str = Field(default="New Conversation")
    status: ConversationStatus = ConversationStatus.ACTIVE
    destination: Optional[str] = None
    travel_dates: Optional[TravelDates] = None
    summary: Optional[str] = None


class ConversationCreate(BaseModel):
    """Create conversation request."""
    agency_id: UUID
    user_id: UUID
    client_id: Optional[UUID] = None
    title: Optional[str] = None


class ConversationUpdate(BaseModel):
    """Update conversation request."""
    title: Optional[str] = None
    status: Optional[ConversationStatus] = None
    destination: Optional[str] = None
    travel_dates: Optional[TravelDates] = None
    summary: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class Conversation(ConversationBase):
    """Complete conversation model (from database)."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    agency_id: UUID
    client_id: Optional[UUID]
    user_id: UUID
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime


class ConversationWithDetails(Conversation):
    """Conversation with related data."""
    client: Optional['Client'] = None
    user: Optional['User'] = None
    message_count: int = 0
    latest_message: Optional['Message'] = None
    has_offer: bool = False


# Forward references
from .client import Client
from .user import User
from .message import Message

ConversationWithDetails.model_rebuild()
