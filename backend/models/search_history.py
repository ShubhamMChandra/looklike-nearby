"""
Search history model for tracking lead generation searches.

WHAT: Defines the SearchHistory SQLAlchemy model for storing search parameters
      and results from Google Places API queries.

WHY: Sales teams need to track their search history to avoid duplicate work,
     understand which searches were most effective, and refine their lead
     generation strategies over time.

HOW: Uses SQLAlchemy model with JSON fields for flexible storage of search
     parameters and results, includes foreign key to reference client,
     and timestamps for historical analysis.

DEPENDENCIES:
- sqlalchemy: ORM functionality and column types
- datetime: Timestamp handling
- typing: Type hints and JSON type
- backend.database.config: Base model class
"""

from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database.config import Base


class SearchHistory(Base):
    """
    Model for storing search history and parameters.
    
    Tracks all searches performed by users, including the reference client,
    search parameters, and number of results found. This enables analytics
    and helps avoid duplicate searches.
    """
    
    __tablename__ = "search_history"
    
    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # Reference to the client used as starting point
    reference_client_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("reference_clients.id", ondelete="SET NULL"),
        index=True
    )
    
    # Search parameters
    search_terms: Mapped[Optional[str]] = mapped_column(Text)  # Comma-separated terms
    radius_meters: Mapped[int] = mapped_column(Integer, nullable=False)
    custom_address: Mapped[Optional[str]] = mapped_column(Text)
    
    # Search filters (stored as JSON for flexibility)
    filters: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    
    # Search results metadata
    results_count: Mapped[int] = mapped_column(Integer, default=0)
    search_duration_seconds: Mapped[Optional[float]] = mapped_column()
    
    # Success metrics
    prospects_added_to_campaigns: Mapped[int] = mapped_column(Integer, default=0)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
        index=True
    )
    
    # Relationships
    reference_client: Mapped[Optional["ReferenceClient"]] = relationship(
        "ReferenceClient"
    )
    
    def __repr__(self) -> str:
        return f"<SearchHistory(id={self.id}, reference_client_id={self.reference_client_id}, results_count={self.results_count})>" 