"""
Referral tracking models for managing prospect referrals.

WHAT: Defines models for tracking referrals between prospects and reference
      clients, including referral status and outcomes.

WHY: Referral tracking is crucial for understanding which reference clients
     generate the most valuable introductions and maintaining the referral
     relationship chain.

HOW: Uses SQLAlchemy models to track referral relationships, communications,
     and outcomes with detailed status tracking.

DEPENDENCIES:
- sqlalchemy: ORM functionality and column types
- datetime: Timestamp handling
- enum: Referral status enumeration
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
    from .campaign import Campaign
    from .reference_client import ReferenceClient
    from .interaction import Interaction


class ReferralStatus(str, Enum):
    """Enumeration of referral process statuses."""
    PLANNED = "planned"
    REQUESTED = "requested"
    APPROVED = "approved"
    INTRODUCED = "introduced"
    DECLINED = "declined"
    CONVERTED = "converted"


class ReferralSource(str, Enum):
    """Enumeration of how the referral was initiated."""
    DIRECT_REQUEST = "direct_request"
    CLIENT_OFFERED = "client_offered"
    PROSPECT_ASKED = "prospect_asked"
    NETWORK_INTRO = "network_intro"


class Referral(Base):
    """
    Model for tracking prospect referrals and their outcomes.
    
    Tracks the complete referral process from request through introduction
    and final outcome, maintaining the relationship chain between
    reference clients and prospects.
    """
    
    __tablename__ = "referrals"
    
    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # Foreign keys
    reference_client_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("reference_clients.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    prospect_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("prospects.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    campaign_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("campaigns.id", ondelete="SET NULL"),
        index=True
    )
    
    # Referral metadata
    status: Mapped[ReferralStatus] = mapped_column(
        SQLEnum(ReferralStatus),
        default=ReferralStatus.PLANNED,
        nullable=False,
        index=True
    )
    source: Mapped[ReferralSource] = mapped_column(
        SQLEnum(ReferralSource),
        nullable=False,
        index=True
    )
    
    # Referral details
    notes: Mapped[Optional[str]] = mapped_column(Text)
    introduction_message: Mapped[Optional[str]] = mapped_column(Text)
    referrer_name: Mapped[Optional[str]] = mapped_column(String(255))
    referrer_title: Mapped[Optional[str]] = mapped_column(String(255))
    referrer_email: Mapped[Optional[str]] = mapped_column(String(255))
    
    # Outcome tracking
    outcome_value: Mapped[Optional[float]] = mapped_column()  # If converted, the deal value
    outcome_notes: Mapped[Optional[str]] = mapped_column(Text)
    
    # Timestamps
    requested_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    introduced_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    converted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
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
    reference_client: Mapped["ReferenceClient"] = relationship("ReferenceClient")
    prospect: Mapped["Prospect"] = relationship("Prospect")
    campaign: Mapped[Optional["Campaign"]] = relationship("Campaign")
    interactions: Mapped[list["Interaction"]] = relationship(
        "Interaction",
        secondary="referral_interactions",
        back_populates="referrals"
    )
    
    def __repr__(self) -> str:
        return f"<Referral(id={self.id}, reference_client_id={self.reference_client_id}, prospect_id={self.prospect_id})>"


class ReferralInteraction(Base):
    """
    Association model linking referrals to their related interactions.
    
    Tracks which interactions are part of the referral process for
    complete referral timeline tracking.
    """
    
    __tablename__ = "referral_interactions"
    
    # Composite primary key
    referral_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("referrals.id", ondelete="CASCADE"),
        primary_key=True
    )
    interaction_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("interactions.id", ondelete="CASCADE"),
        primary_key=True
    )
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False
    )
    
    def __repr__(self) -> str:
        return f"<ReferralInteraction(referral_id={self.referral_id}, interaction_id={self.interaction_id})>"