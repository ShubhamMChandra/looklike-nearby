"""
Interaction model for tracking all prospect communications and activities.

WHAT: Defines models for tracking all types of interactions with prospects,
      including emails, calls, meetings, and other activities.

WHY: CRM functionality requires detailed tracking of all communications and
     activities with prospects to maintain a complete history of the
     relationship.

HOW: Uses SQLAlchemy models with polymorphic inheritance to handle different
     types of interactions (emails, calls, meetings) while maintaining a
     unified activity timeline.

DEPENDENCIES:
- sqlalchemy: ORM functionality and column types
- datetime: Timestamp handling
- enum: Interaction type and status enums
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


class InteractionType(str, Enum):
    """Enumeration of different types of prospect interactions."""
    EMAIL = "email"
    CALL = "call"
    MEETING = "meeting"
    NOTE = "note"
    TASK = "task"
    REFERRAL = "referral"


class InteractionDirection(str, Enum):
    """Enumeration of interaction directions."""
    INBOUND = "inbound"
    OUTBOUND = "outbound"
    INTERNAL = "internal"


class InteractionStatus(str, Enum):
    """Enumeration of interaction statuses."""
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Interaction(Base):
    """
    Base model for tracking all types of prospect interactions.
    
    This model serves as the foundation for tracking all communications
    and activities with prospects, providing a complete timeline of
    the relationship.
    """
    
    __tablename__ = "interactions"
    
    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # Foreign keys
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
    
    # Interaction metadata
    type: Mapped[InteractionType] = mapped_column(
        SQLEnum(InteractionType),
        nullable=False,
        index=True
    )
    direction: Mapped[InteractionDirection] = mapped_column(
        SQLEnum(InteractionDirection),
        nullable=False,
        index=True
    )
    status: Mapped[InteractionStatus] = mapped_column(
        SQLEnum(InteractionStatus),
        default=InteractionStatus.COMPLETED,
        nullable=False,
        index=True
    )
    
    # Content and scheduling
    subject: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    scheduled_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    
    # Additional metadata
    contact_name: Mapped[Optional[str]] = mapped_column(String(255))
    contact_title: Mapped[Optional[str]] = mapped_column(String(255))
    contact_email: Mapped[Optional[str]] = mapped_column(String(255))
    contact_phone: Mapped[Optional[str]] = mapped_column(String(50))
    
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
    prospect: Mapped["Prospect"] = relationship(
        "Prospect",
        back_populates="interactions"
    )
    campaign: Mapped[Optional["Campaign"]] = relationship(
        "Campaign",
        back_populates="interactions"
    )
    
    def __repr__(self) -> str:
        return f"<Interaction(id={self.id}, type='{self.type}', prospect_id={self.prospect_id})>"