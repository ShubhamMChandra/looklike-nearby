"""
Email template models for managing reusable email content.

WHAT: Defines models for storing and managing email templates and tracking
      their usage in prospect communications.

WHY: Sales teams need standardized templates for common communications,
     with the ability to track which templates are most effective.

HOW: Uses SQLAlchemy models to store template content with variable
     placeholders and tracks template usage statistics.

DEPENDENCIES:
- sqlalchemy: ORM functionality and column types
- datetime: Timestamp handling
- backend.database.config: Base model class
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Integer, String, Text, text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database.config import Base


class EmailTemplate(Base):
    """
    Model for storing reusable email templates.
    
    Templates can include variable placeholders that get replaced with
    prospect-specific information when used.
    """
    
    __tablename__ = "email_templates"
    
    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # Template metadata
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text)
    category: Mapped[Optional[str]] = mapped_column(String(100), index=True)
    
    # Template content
    subject: Mapped[str] = mapped_column(String(255), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Usage statistics
    times_used: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_used_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    
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
        return f"<EmailTemplate(id={self.id}, name='{self.name}')>"


class EmailTemplateUsage(Base):
    """
    Model for tracking when and how email templates are used.
    
    Records each instance of template usage with prospect and campaign
    context for effectiveness analysis.
    """
    
    __tablename__ = "email_template_usage"
    
    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # Foreign keys
    template_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("email_templates.id", ondelete="CASCADE"),
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
    interaction_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("interactions.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Usage metadata
    variables_used: Mapped[Optional[str]] = mapped_column(Text)  # JSON string of variables
    customizations: Mapped[Optional[str]] = mapped_column(Text)  # Track template modifications
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False
    )
    
    # Relationships
    template: Mapped["EmailTemplate"] = relationship("EmailTemplate")
    prospect: Mapped["Prospect"] = relationship("Prospect")
    campaign: Mapped[Optional["Campaign"]] = relationship("Campaign")
    interaction: Mapped["Interaction"] = relationship("Interaction")
    
    def __repr__(self) -> str:
        return f"<EmailTemplateUsage(id={self.id}, template_id={self.template_id}, prospect_id={self.prospect_id})>"