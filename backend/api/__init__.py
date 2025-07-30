"""
API route handlers for the lead generation platform.

WHAT: Contains FastAPI route handlers organized by functionality area
      (authentication, reference clients, campaigns, search, prospects).

WHY: Provides clean separation of API endpoints with proper organization,
     error handling, and authentication middleware for all client-server
     communication.

HOW: Uses FastAPI routers with dependency injection for database sessions,
     authentication, and request validation through Pydantic models.

DEPENDENCIES:
- All router modules from individual API files
"""

from .auth import router as auth_router
from .campaigns import router as campaigns_router
from .prospects import router as prospects_router
from .reference_clients import router as reference_clients_router
from .search import router as search_router

__all__ = [
    "auth_router",
    "reference_clients_router", 
    "search_router",
    "prospects_router",
    "campaigns_router",
] 