"""
Database models for the lead generation platform.

WHAT: Defines SQLAlchemy ORM models for reference clients, campaigns,
      prospects, and related data structures.

WHY: Provides structured data storage and relationships for the lead
     generation workflow, enabling persistent storage of client data,
     search history, and prospect management.

HOW: Uses SQLAlchemy 2.0 declarative models with proper relationships,
     indexes, and constraints to ensure data integrity and performance.

DEPENDENCIES:
- All model classes from individual model files
"""

from .reference_client import ReferenceClient
from .search_history import SearchHistory
from .interaction import Interaction
from .referral import Referral, ReferralInteraction
from .email_template import EmailTemplate, EmailTemplateUsage
from .prospect import Prospect
from .campaign import Campaign, CampaignProspect

__all__ = [
    "ReferenceClient",
    "SearchHistory",
    "Interaction",
    "Referral",
    "ReferralInteraction",
    "EmailTemplate",
    "EmailTemplateUsage",
    "Prospect",
    "Campaign",
    "CampaignProspect",
] 