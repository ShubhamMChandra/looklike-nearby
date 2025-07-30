"""
Prospect model for storing potential business leads.

WHAT: Defines the Prospect SQLAlchemy model for storing business information
      retrieved from Google Places API searches.

WHY: Sales teams need to store and manage potential prospects discovered
     through geographic searches, including contact information, ratings,
     and business details for outreach campaigns.

HOW: Uses SQLAlchemy model with Google Places data fields, geographic
     coordinates, and unique constraints on place_id to prevent duplicates.
     Includes relationships to campaigns for organization.

DEPENDENCIES:
- sqlalchemy: ORM functionality and column types
- datetime: Timestamp handling
- typing: Type hints and forward references
- backend.database.config: Base model class
"""

from datetime import datetime
from typing import Optional, TYPE_CHECKING

from sqlalchemy import DateTime, Float, Integer, String, Text, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database.config import Base

if TYPE_CHECKING:
    from .campaign import CampaignProspect


class Prospect(Base):
    """
    Model for storing prospect business information from Google Places API.
    
    Prospects are potential customers discovered through geographic searches
    around reference clients. This model stores all relevant business data
    needed for sales outreach.
    """
    
    __tablename__ = "prospects"
    __table_args__ = (
        UniqueConstraint("place_id", name="uq_prospect_place_id"),
    )
    
    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # Google Places API identifier (unique)
    place_id: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    
    # Basic business information
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    address: Mapped[str] = mapped_column(Text, nullable=False)
    business_type: Mapped[Optional[str]] = mapped_column(String(100), index=True)
    
    # Geographic coordinates
    latitude: Mapped[Optional[float]] = mapped_column(Float)
    longitude: Mapped[Optional[float]] = mapped_column(Float)
    
    # Contact information
    phone: Mapped[Optional[str]] = mapped_column(String(50))
    website: Mapped[Optional[str]] = mapped_column(String(500))
    email: Mapped[Optional[str]] = mapped_column(String(255))
    
    # Additional CRM contact fields
    primary_contact_name: Mapped[Optional[str]] = mapped_column(String(255))
    primary_contact_title: Mapped[Optional[str]] = mapped_column(String(255))
    primary_contact_email: Mapped[Optional[str]] = mapped_column(String(255))
    primary_contact_phone: Mapped[Optional[str]] = mapped_column(String(50))
    secondary_contact_name: Mapped[Optional[str]] = mapped_column(String(255))
    secondary_contact_title: Mapped[Optional[str]] = mapped_column(String(255))
    secondary_contact_email: Mapped[Optional[str]] = mapped_column(String(255))
    secondary_contact_phone: Mapped[Optional[str]] = mapped_column(String(50))
    
    # Company information
    employee_count: Mapped[Optional[int]] = mapped_column(Integer)
    annual_revenue: Mapped[Optional[float]] = mapped_column(Float)
    year_founded: Mapped[Optional[int]] = mapped_column(Integer)
    linkedin_url: Mapped[Optional[str]] = mapped_column(String(500))
    facebook_url: Mapped[Optional[str]] = mapped_column(String(500))
    twitter_url: Mapped[Optional[str]] = mapped_column(String(500))
    
    # Sales information
    lead_source: Mapped[Optional[str]] = mapped_column(String(100))
    lead_score: Mapped[Optional[int]] = mapped_column(Integer)
    estimated_value: Mapped[Optional[float]] = mapped_column(Float)
    next_follow_up: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    last_contacted: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    
    # Google Places metadata
    rating: Mapped[Optional[float]] = mapped_column(Float)
    price_level: Mapped[Optional[int]] = mapped_column(Integer)
    user_ratings_total: Mapped[Optional[int]] = mapped_column(Integer)
    
    # Business status and hours
    is_open_now: Mapped[Optional[bool]] = mapped_column()
    permanently_closed: Mapped[Optional[bool]] = mapped_column(default=False)
    
    # Additional metadata
    formatted_address: Mapped[Optional[str]] = mapped_column(Text)
    international_phone_number: Mapped[Optional[str]] = mapped_column(String(50))
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        onupdate=text("CURRENT_TIMESTAMP"),
        nullable=False
    )
    
    # Relationships
    campaign_prospects: Mapped[list["CampaignProspect"]] = relationship(
        "CampaignProspect",
        back_populates="prospect",
        cascade="all, delete-orphan"
    )
    # Temporarily disabled to fix initialization issues
    # interactions: Mapped[list["Interaction"]] = relationship(
    #     "Interaction",
    #     back_populates="prospect",
    #     cascade="all, delete-orphan"
    # )
    # referrals: Mapped[list["Referral"]] = relationship(
    #     "Referral",
    #     back_populates="prospect",
    #     cascade="all, delete-orphan"
    # )
    # template_usage: Mapped[list["EmailTemplateUsage"]] = relationship(
    #     "EmailTemplateUsage",
    #     back_populates="prospect",
    #     cascade="all, delete-orphan"
    # )
    
    def __repr__(self) -> str:
        return f"<Prospect(id={self.id}, name='{self.name}', place_id='{self.place_id}')>" 