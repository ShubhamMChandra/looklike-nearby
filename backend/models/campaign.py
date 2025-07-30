"""
Campaign models for organizing prospect lists and tracking outreach.

WHAT: Defines Campaign and CampaignProspect models for organizing prospects
      into named campaigns and tracking their status through the sales funnel.

WHY: Sales teams need to organize prospects into campaigns (e.g., "Q1 2025 Chicago"),
     track outreach status, and maintain notes about each prospect's progress
     through the sales process.

HOW: Uses SQLAlchemy models with many-to-many relationship between campaigns
     and prospects, includes status tracking, notes, and reference client
     associations for context.

DEPENDENCIES:
- sqlalchemy: ORM functionality and column types
- datetime: Timestamp handling
- enum: Status enumeration
- backend.database.config: Base model class
"""

from datetime import datetime
from enum import Enum
from typing import Optional, TYPE_CHECKING

from sqlalchemy import DateTime, Enum as SQLEnum, ForeignKey, Integer, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database.config import Base

if TYPE_CHECKING:
    from .prospect import Prospect
    from .reference_client import ReferenceClient


class ProspectStatus(str, Enum):
    """Enumeration of prospect statuses in the sales funnel."""
    NEW = "new"
    CONTACTED = "contacted"
    QUALIFIED = "qualified"
    NOT_INTERESTED = "not_interested"
    CONVERTED = "converted"


class Campaign(Base):
    """
    Model for organizing prospects into named campaigns.
    
    Campaigns allow sales teams to group prospects by territory,
    time period, or other business criteria for organized outreach.
    """
    
    __tablename__ = "campaigns"
    
    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # Campaign metadata
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text)
    
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
        back_populates="campaign",
        cascade="all, delete-orphan"
    )
    # Temporarily disabled to fix initialization issues
    # interactions: Mapped[list["Interaction"]] = relationship(
    #     "Interaction",
    #     back_populates="campaign",
    #     cascade="all, delete-orphan"
    # )
    
    def __repr__(self) -> str:
        return f"<Campaign(id={self.id}, name='{self.name}')>"


class CampaignProspect(Base):
    """
    Association model linking campaigns to prospects with status tracking.
    
    This model represents the many-to-many relationship between campaigns
    and prospects, with additional fields for tracking outreach status
    and maintaining notes about each prospect.
    """
    
    __tablename__ = "campaign_prospects"
    
    # Composite primary key
    campaign_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("campaigns.id", ondelete="CASCADE"),
        primary_key=True
    )
    prospect_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("prospects.id", ondelete="CASCADE"),
        primary_key=True
    )
    
    # Reference client association for context
    reference_client_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("reference_clients.id", ondelete="SET NULL")
    )
    
    # Status tracking
    status: Mapped[ProspectStatus] = mapped_column(
        SQLEnum(ProspectStatus),
        default=ProspectStatus.NEW,
        nullable=False,
        index=True
    )
    
    # Notes and metadata
    notes: Mapped[Optional[str]] = mapped_column(Text)
    
    # Timestamps
    added_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False
    )
    status_updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        onupdate=text("CURRENT_TIMESTAMP"),
        nullable=False
    )
    
    # Relationships
    campaign: Mapped["Campaign"] = relationship(
        "Campaign",
        back_populates="campaign_prospects"
    )
    prospect: Mapped["Prospect"] = relationship(
        "Prospect",
        back_populates="campaign_prospects"
    )
    reference_client: Mapped[Optional["ReferenceClient"]] = relationship(
        "ReferenceClient"
    )
    
    def __repr__(self) -> str:
        return f"<CampaignProspect(campaign_id={self.campaign_id}, prospect_id={self.prospect_id}, status='{self.status}')>" 