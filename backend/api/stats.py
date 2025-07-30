"""
Stats API routes for dashboard metrics.

WHAT: Provides FastAPI routes for fetching dashboard statistics
      like total clients, campaigns, prospects, and searches.

WHY: Dashboard needs overview metrics to display to users.

HOW: Queries database tables and returns counts.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func
from sqlalchemy.future import select

from backend.auth.password_auth import RequireAuth
from backend.database.config import get_db
from backend.models.reference_client import ReferenceClient
from backend.models.campaign import Campaign
from backend.models.prospect import Prospect
from backend.models.search_history import SearchHistory

router = APIRouter()


@router.get("/")
async def get_stats(
    db: AsyncSession = Depends(get_db),
    _: str = RequireAuth
) -> dict:
    """
    Get dashboard statistics.
    
    Returns:
        Dictionary with counts for reference clients, campaigns, prospects, and searches
    """
    try:
        # Count reference clients
        clients_result = await db.execute(select(func.count(ReferenceClient.id)))
        clients_count = clients_result.scalar() or 0
        
        # Count campaigns
        campaigns_result = await db.execute(select(func.count(Campaign.id)))
        campaigns_count = campaigns_result.scalar() or 0
        
        # Count prospects
        prospects_result = await db.execute(select(func.count(Prospect.id)))
        prospects_count = prospects_result.scalar() or 0
        
        # Count searches
        searches_result = await db.execute(select(func.count(SearchHistory.id)))
        searches_count = searches_result.scalar() or 0
        
        return {
            "referenceClients": clients_count,
            "campaigns": campaigns_count,
            "prospects": prospects_count,
            "searches": searches_count
        }
    except Exception as e:
        return {
            "referenceClients": 0,
            "campaigns": 0,
            "prospects": 0,
            "searches": 0
        }