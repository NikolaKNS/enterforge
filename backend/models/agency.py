"""
Agency (tenant) models.
"""

from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict


class AgencyBranding(BaseModel):
    """Agency branding configuration."""
    primary_color: str = Field(default="#E85D04", pattern=r"^#[0-9A-Fa-f]{6}$")
    logo_url: Optional[str] = None
    email_template: str = "default"
    company_name: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None


class AgencySettings(BaseModel):
    """Agency settings and defaults."""
    default_markup_percent: float = Field(default=10.0, ge=0, le=100)
    currency: str = Field(default="EUR", pattern=r"^[A-Z]{3}$")
    timezone: str = "Europe/Berlin"
    default_pdf_template: str = "standard"
    email_signature: Optional[str] = None


class AgencyBase(BaseModel):
    """Base agency model."""
    name: str = Field(..., min_length=1, max_length=255)
    slug: str = Field(..., min_length=1, max_length=100, pattern=r"^[a-z0-9-]+$")
    branding_config: AgencyBranding = Field(default_factory=AgencyBranding)
    settings: AgencySettings = Field(default_factory=AgencySettings)


class AgencyCreate(AgencyBase):
    """Create agency request."""
    pass


class AgencyUpdate(BaseModel):
    """Update agency request."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    branding_config: Optional[AgencyBranding] = None
    settings: Optional[AgencySettings] = None


class Agency(AgencyBase):
    """Complete agency model (from database)."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
    updated_at: datetime

    def get_branding(self) -> AgencyBranding:
        """Get branding with defaults."""
        return self.branding_config or AgencyBranding()

    def get_settings(self) -> AgencySettings:
        """Get settings with defaults."""
        return self.settings or AgencySettings()
