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

from .campaign import Campaign, CampaignProspect
from .interaction import Interaction
from .prospect import Prospect
from .reference_client import ReferenceClient
from .search_history import SearchHistory

__all__ = [
    "ReferenceClient",
    "SearchHistory", 
    "Campaign",
    "Prospect",
    "CampaignProspect",
    "Interaction",
] 