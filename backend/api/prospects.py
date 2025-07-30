"""
Prospects API routes for managing potential business leads.

WHAT: Provides FastAPI routes for storing and managing prospect data
      discovered through Google Places API searches.

WHY: Sales teams need to store, organize, and track potential prospects
     discovered through geographic searches for future outreach campaigns.

HOW: Uses FastAPI routers with async database operations, Google Places
     data integration, and Pydantic models for request/response validation.

DEPENDENCIES:
- fastapi: Router and HTTP handling
- sqlalchemy: Database operations
- pydantic: Request/response validation
- backend.models: Database models
- backend.database: Database session management
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend.auth.password_auth import RequireAuth
from backend.database.config import get_db
from backend.models.prospect import Prospect

router = APIRouter()


class ProspectCreate(BaseModel):
    """Request model for creating prospects."""
    place_id: str
    name: str
    address: str
    business_type: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    email: Optional[str] = None
    rating: Optional[float] = None
    price_level: Optional[int] = None
    user_ratings_total: Optional[int] = None
    is_open_now: Optional[bool] = None
    permanently_closed: Optional[bool] = None
    formatted_address: Optional[str] = None
    international_phone_number: Optional[str] = None


class ProspectUpdate(BaseModel):
    """Request model for updating prospects."""
    name: Optional[str] = None
    address: Optional[str] = None
    business_type: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    email: Optional[str] = None
    rating: Optional[float] = None
    permanently_closed: Optional[bool] = None


class ProspectResponse(BaseModel):
    """Response model for prospect data."""
    id: int
    place_id: str
    name: str
    address: str
    business_type: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    phone: Optional[str]
    website: Optional[str]
    email: Optional[str]
    rating: Optional[float]
    price_level: Optional[int]
    user_ratings_total: Optional[int]
    is_open_now: Optional[bool]
    permanently_closed: Optional[bool]
    formatted_address: Optional[str]
    international_phone_number: Optional[str]
    
    class Config:
        from_attributes = True


class ProspectsListResponse(BaseModel):
    """Response model for prospects list."""
    prospects: List[ProspectResponse]
    total: int


@router.get("", response_model=ProspectsListResponse)
async def get_prospects(
    limit: int = 100,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    _: str = RequireAuth
) -> ProspectsListResponse:
    """
    Get all prospects with pagination.
    
    Args:
        limit: Maximum number of results to return
        offset: Number of results to skip
        db: Database session
        _: Authentication dependency
        
    Returns:
        List of prospects
    """
    try:
        result = await db.execute(
            select(Prospect).offset(offset).limit(limit)
        )
        prospects = result.scalars().all()
        
        # Get total count
        count_result = await db.execute(select(Prospect))
        total = len(count_result.scalars().all())
        
        return ProspectsListResponse(
            prospects=[ProspectResponse.model_validate(prospect) for prospect in prospects],
            total=total
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch prospects: {str(e)}"
        )


@router.post("", response_model=ProspectResponse, status_code=status.HTTP_201_CREATED)
async def create_prospect(
    prospect_data: ProspectCreate,
    db: AsyncSession = Depends(get_db),
    _: str = RequireAuth
) -> ProspectResponse:
    """
    Create a new prospect.
    
    Args:
        prospect_data: Prospect data
        db: Database session
        _: Authentication dependency
        
    Returns:
        Created prospect
    """
    try:
        # Check if prospect with same place_id already exists
        existing_result = await db.execute(
            select(Prospect).where(Prospect.place_id == prospect_data.place_id)
        )
        existing_prospect = existing_result.scalar_one_or_none()
        
        if existing_prospect:
            return ProspectResponse.model_validate(existing_prospect)
        
        # Create new prospect
        prospect = Prospect(**prospect_data.model_dump())
        db.add(prospect)
        await db.commit()
        await db.refresh(prospect)
        
        return ProspectResponse.model_validate(prospect)
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create prospect: {str(e)}"
        )


@router.get("/{prospect_id}", response_model=ProspectResponse)
async def get_prospect(
    prospect_id: int,
    db: AsyncSession = Depends(get_db),
    _: str = RequireAuth
) -> ProspectResponse:
    """
    Get a specific prospect by ID.
    
    Args:
        prospect_id: Prospect ID
        db: Database session
        _: Authentication dependency
        
    Returns:
        Prospect data
        
    Raises:
        HTTPException: If prospect not found (404)
    """
    try:
        result = await db.execute(select(Prospect).where(Prospect.id == prospect_id))
        prospect = result.scalar_one_or_none()
        
        if not prospect:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Prospect not found"
            )
        
        return ProspectResponse.model_validate(prospect)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch prospect: {str(e)}"
        )


@router.get("/by-place-id/{place_id}", response_model=ProspectResponse)
async def get_prospect_by_place_id(
    place_id: str,
    db: AsyncSession = Depends(get_db),
    _: str = RequireAuth
) -> ProspectResponse:
    """
    Get a specific prospect by Google Places ID.
    
    Args:
        place_id: Google Places place_id
        db: Database session
        _: Authentication dependency
        
    Returns:
        Prospect data
        
    Raises:
        HTTPException: If prospect not found (404)
    """
    try:
        result = await db.execute(select(Prospect).where(Prospect.place_id == place_id))
        prospect = result.scalar_one_or_none()
        
        if not prospect:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Prospect not found"
            )
        
        return ProspectResponse.model_validate(prospect)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch prospect: {str(e)}"
        )


@router.put("/{prospect_id}", response_model=ProspectResponse)
async def update_prospect(
    prospect_id: int,
    prospect_data: ProspectUpdate,
    db: AsyncSession = Depends(get_db),
    _: str = RequireAuth
) -> ProspectResponse:
    """
    Update a prospect.
    
    Args:
        prospect_id: Prospect ID
        prospect_data: Updated prospect data
        db: Database session
        _: Authentication dependency
        
    Returns:
        Updated prospect
        
    Raises:
        HTTPException: If prospect not found (404)
    """
    try:
        result = await db.execute(select(Prospect).where(Prospect.id == prospect_id))
        prospect = result.scalar_one_or_none()
        
        if not prospect:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Prospect not found"
            )
        
        # Update only provided fields
        update_data = prospect_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(prospect, field, value)
        
        await db.commit()
        await db.refresh(prospect)
        
        return ProspectResponse.model_validate(prospect)
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update prospect: {str(e)}"
        )


@router.delete("/{prospect_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_prospect(
    prospect_id: int,
    db: AsyncSession = Depends(get_db),
    _: str = RequireAuth
) -> None:
    """
    Delete a prospect.
    
    Args:
        prospect_id: Prospect ID
        db: Database session
        _: Authentication dependency
        
    Raises:
        HTTPException: If prospect not found (404)
    """
    try:
        result = await db.execute(select(Prospect).where(Prospect.id == prospect_id))
        prospect = result.scalar_one_or_none()
        
        if not prospect:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Prospect not found"
            )
        
        await db.delete(prospect)
        await db.commit()
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete prospect: {str(e)}"
        )