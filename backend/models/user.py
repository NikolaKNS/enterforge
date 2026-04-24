"""
User (agency staff) models.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID
from enum import Enum
from pydantic import BaseModel, Field, EmailStr, ConfigDict


class UserRole(str, Enum):
    """User roles within an agency."""
    ADMIN = "admin"
    AGENT = "agent"


class UserPreferences(BaseModel):
    """User-specific preferences."""
    default_client_view: str = "grid"  # grid or list
    email_notifications: bool = True
    browser_notifications: bool = True
    theme: str = "light"  # light or dark
    default_currency: Optional[str] = None


class UserBase(BaseModel):
    """Base user model."""
    email: EmailStr
    name: str = Field(..., min_length=1, max_length=255)
    role: UserRole
    is_active: bool = True


class UserCreate(UserBase):
    """Create user request."""
    agency_id: UUID
    auth_user_id: Optional[UUID] = None
    preferences: UserPreferences = Field(default_factory=UserPreferences)


class UserUpdate(BaseModel):
    """Update user request."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None
    preferences: Optional[UserPreferences] = None


class User(UserBase):
    """Complete user model (from database)."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    agency_id: UUID
    auth_user_id: Optional[UUID]
    preferences: UserPreferences
    created_at: datetime
    updated_at: datetime

    @property
    def is_admin(self) -> bool:
        """Check if user is admin."""
        return self.role == UserRole.ADMIN

    @property
    def full_name(self) -> str:
        """Get user full name."""
        return self.name
