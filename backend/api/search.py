"""
Search API routes for finding similar businesses using Google Places.

WHAT: Provides FastAPI routes for searching similar businesses around
      reference clients using Google Places API integration.

WHY: Sales teams need to discover potential prospects by searching for
     businesses similar to their successful clients within specific
     geographic areas.

HOW: Uses FastAPI routers with Google Places API integration, geocoding,
     and business similarity matching algorithms from the leadgen package.

DEPENDENCIES:
- fastapi: Router and HTTP handling
- leadgen: Core business logic for Google Places integration
- backend.models: Database models for storing search history
- backend.database: Database session management
"""

import os
import time
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend.auth.password_auth import RequireAuth
from backend.database.config import get_db
from backend.models.reference_client import ReferenceClient
from backend.models.search_history import SearchHistory
from leadgen import google_places as gp

router = APIRouter()


class SearchRequest(BaseModel):
    """Request model for business search."""
    reference_client_id: Optional[int] = None
    business_name: Optional[str] = None
    address: Optional[str] = None
    business_type: Optional[str] = None
    radius_miles: int = 10
    custom_address: Optional[str] = None
    custom_industry: Optional[str] = None


class ProspectResult(BaseModel):
    """Response model for individual prospect results."""
    place_id: str
    name: str
    address: str
    business_type: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    rating: Optional[float] = None
    distance: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class SearchResponse(BaseModel):
    """Response model for search results."""
    results: List[ProspectResult]
    count: int
    search_parameters: dict
    reference_client: Optional[dict] = None


@router.post("/prospects", response_model=SearchResponse)
async def search_prospects(
    search_request: SearchRequest,
    db: AsyncSession = Depends(get_db),
    _: str = RequireAuth
) -> SearchResponse:
    """
    Search for similar businesses using Google Places API.
    
    Args:
        search_request: Search parameters
        db: Database session
        _: Authentication dependency
        
    Returns:
        List of similar businesses found
        
    Raises:
        HTTPException: If search fails or invalid parameters
    """
    start_time = time.time()
    
    try:
        # Get Google API key
        google_api_key = os.getenv("GOOGLE_API_KEY")
        if not google_api_key:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Google API key not configured"
            )
        
        # Determine search address and terms
        reference_client = None
        if search_request.reference_client_id:
            # Use reference client data
            result = await db.execute(
                select(ReferenceClient).where(ReferenceClient.id == search_request.reference_client_id)
            )
            reference_client = result.scalar_one_or_none()
            
            if not reference_client:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Reference client not found"
                )
            
            address = search_request.custom_address or reference_client.address
            search_terms = []
            
            if search_request.custom_industry:
                search_terms = [term.strip() for term in search_request.custom_industry.split(",")]
            else:
                if reference_client.business_type:
                    search_terms.append(reference_client.business_type)
        else:
            # Use provided business data
            if not search_request.business_name or not search_request.address:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Either reference_client_id or business_name+address must be provided"
                )
            
            address = search_request.address
            search_terms = []
            if search_request.business_type:
                search_terms.append(search_request.business_type)
        
        if not search_terms:
            search_terms = ["business"]  # Fallback search term
        
        # Convert radius to meters
        radius_meters = int(search_request.radius_miles * 1609.34)
        
        # Search for similar businesses
        try:
            results = gp.find_similar_businesses(
                google_api_key,
                address,
                search_terms,
                radius_meters
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Google Places API error: {str(e)}"
            )
        
        # Convert results to response format
        prospect_results = []
        for result in results:
            # Extract business type from Google Places types
            business_type = None
            if "types" in result:
                types = [t.replace("_", " ").title() for t in result["types"] 
                        if t not in ["point_of_interest", "establishment"]]
                business_type = ", ".join(types[:2]) if types else None
            
            # Get coordinates
            lat, lng = None, None
            if "geometry" in result and "location" in result["geometry"]:
                lat = result["geometry"]["location"].get("lat")
                lng = result["geometry"]["location"].get("lng")
            
            prospect_results.append(ProspectResult(
                place_id=result.get("place_id", ""),
                name=result.get("name", "Unknown"),
                address=result.get("formatted_address", result.get("vicinity", "")),
                business_type=business_type,
                phone=result.get("formatted_phone_number"),
                website=result.get("website"),
                rating=result.get("rating"),
                distance=None,  # TODO: Calculate distance
                latitude=lat,
                longitude=lng
            ))
        
        # Log search to history
        search_duration = time.time() - start_time
        search_history = SearchHistory(
            reference_client_id=search_request.reference_client_id,
            search_terms=",".join(search_terms),
            radius_meters=radius_meters,
            custom_address=search_request.custom_address,
            results_count=len(prospect_results),
            search_duration_seconds=search_duration
        )
        db.add(search_history)
        await db.commit()
        
        # Build response
        reference_client_data = None
        if reference_client:
            reference_client_data = {
                "id": reference_client.id,
                "name": reference_client.name,
                "address": reference_client.address,
                "business_type": reference_client.business_type
            }
        
        return SearchResponse(
            results=prospect_results,
            count=len(prospect_results),
            search_parameters={
                "address": address,
                "search_terms": search_terms,
                "radius_miles": search_request.radius_miles,
                "radius_meters": radius_meters
            },
            reference_client=reference_client_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}"
        )


@router.get("/history")
async def get_search_history(
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    _: str = RequireAuth
) -> dict:
    """
    Get recent search history.
    
    Args:
        limit: Maximum number of results to return
        db: Database session
        _: Authentication dependency
        
    Returns:
        List of recent searches
    """
    try:
        result = await db.execute(
            select(SearchHistory)
            .order_by(SearchHistory.created_at.desc())
            .limit(limit)
        )
        searches = result.scalars().all()
        
        return {
            "searches": [
                {
                    "id": search.id,
                    "search_terms": search.search_terms,
                    "radius_meters": search.radius_meters,
                    "results_count": search.results_count,
                    "created_at": search.created_at.isoformat(),
                    "reference_client_id": search.reference_client_id
                }
                for search in searches
            ],
            "total": len(searches)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch search history: {str(e)}"
        )