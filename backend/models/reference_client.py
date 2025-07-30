"""
Reference client model for storing existing client information.

WHAT: Defines the ReferenceClient SQLAlchemy model for storing information
      about existing clients that serve as reference points for finding
      similar businesses.

WHY: Sales teams need to store and manage their successful client relationships
     to use as starting points for lead generation searches. These reference
     clients provide the geographic and business context for finding prospects.

HOW: Uses SQLAlchemy model with geographic coordinates, business metadata,
     and timestamps. Includes indexes on commonly queried fields for
     performance optimization.

DEPENDENCIES:
- sqlalchemy: ORM functionality and column types
- datetime: Timestamp handling
- backend.database.config: Base model class
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Float, Integer, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column

from backend.database.config import Base


class ReferenceClient(Base):
    """
    Model for storing reference client information.
    
    Reference clients are existing successful clients that serve as
    starting points for finding similar businesses in the same area.
    """
    
    __tablename__ = "reference_clients"
    
    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # Basic business information
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    address: Mapped[str] = mapped_column(Text, nullable=False)
    business_type: Mapped[Optional[str]] = mapped_column(String(100), index=True)
    
    # Geographic coordinates for radius searches
    latitude: Mapped[Optional[float]] = mapped_column(Float)
    longitude: Mapped[Optional[float]] = mapped_column(Float)
    
    # Additional metadata
    notes: Mapped[Optional[str]] = mapped_column(Text)
    
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
    
    def __repr__(self) -> str:
        return f"<ReferenceClient(id={self.id}, name='{self.name}', business_type='{self.business_type}')>" 