"""
Client (traveler) models.
"""

from datetime import datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field, EmailStr, ConfigDict


class ClientPreferences(BaseModel):
    """Client travel preferences."""
    budget_range: Optional[str] = None  # budget, mid-range, luxury
    travel_style: Optional[str] = None  # adventure, relaxation, cultural, etc.
    dietary_restrictions: List[str] = Field(default_factory=list)
    accessibility_needs: Optional[str] = None
    preferred_airlines: List[str] = Field(default_factory=list)
    seat_preference: Optional[str] = None  # window, aisle, etc.
    room_preference: Optional[str] = None  # suite, standard, etc.
    activity_level: Optional[str] = None  # low, medium, high


class ClientBase(BaseModel):
    """Base client model."""
    name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr
    phone: Optional[str] = None
    preferences: ClientPreferences = Field(default_factory=ClientPreferences)
    notes: Optional[str] = None


class ClientCreate(ClientBase):
    """Create client request."""
    agency_id: UUID
    created_by: Optional[UUID] = None


class ClientUpdate(BaseModel):
    """Update client request."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    preferences: Optional[ClientPreferences] = None
    notes: Optional[str] = None


class Client(ClientBase):
    """Complete client model (from database)."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    agency_id: UUID
    created_by: Optional[UUID]
    created_at: datetime
    updated_at: datetime


class ClientWithStats(Client):
    """Client with additional statistics."""
    total_offers: int = 0
    total_bookings: int = 0
    last_contact_date: Optional[datetime] = None
