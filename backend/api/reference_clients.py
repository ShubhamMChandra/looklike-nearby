"""
Reference clients API routes for managing successful client data.

WHAT: Provides FastAPI routes for CRUD operations on reference clients
      that serve as starting points for lead generation searches.

WHY: Sales teams need to manage their successful client relationships
     to use as reference points for finding similar businesses in
     geographic areas.

HOW: Uses FastAPI routers with async database operations, proper error
     handling, and Pydantic models for request/response validation.

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
from backend.models.reference_client import ReferenceClient

router = APIRouter()


class ReferenceClientCreate(BaseModel):
    """Request model for creating reference clients."""
    name: str
    address: str
    business_type: Optional[str] = None
    notes: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class ReferenceClientUpdate(BaseModel):
    """Request model for updating reference clients."""
    name: Optional[str] = None
    address: Optional[str] = None
    business_type: Optional[str] = None
    notes: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class ReferenceClientResponse(BaseModel):
    """Response model for reference client data."""
    id: int
    name: str
    address: str
    business_type: Optional[str]
    notes: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    
    class Config:
        from_attributes = True


class ReferenceClientsListResponse(BaseModel):
    """Response model for reference clients list."""
    clients: List[ReferenceClientResponse]
    total: int


@router.get("", response_model=ReferenceClientsListResponse)
async def get_reference_clients(
    db: AsyncSession = Depends(get_db),
    _: str = RequireAuth
) -> ReferenceClientsListResponse:
    """
    Get all reference clients.
    
    Args:
        db: Database session
        _: Authentication dependency
        
    Returns:
        List of all reference clients
    """
    try:
        result = await db.execute(select(ReferenceClient))
        clients = result.scalars().all()
        
        return ReferenceClientsListResponse(
            clients=[ReferenceClientResponse.model_validate(client) for client in clients],
            total=len(clients)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch reference clients: {str(e)}"
        )


@router.post("", response_model=ReferenceClientResponse, status_code=status.HTTP_201_CREATED)
async def create_reference_client(
    client_data: ReferenceClientCreate,
    db: AsyncSession = Depends(get_db),
    _: str = RequireAuth
) -> ReferenceClientResponse:
    """
    Create a new reference client.
    
    Args:
        client_data: Reference client data
        db: Database session
        _: Authentication dependency
        
    Returns:
        Created reference client
    """
    try:
        # Create new reference client
        client = ReferenceClient(**client_data.model_dump())
        db.add(client)
        await db.commit()
        await db.refresh(client)
        
        return ReferenceClientResponse.model_validate(client)
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create reference client: {str(e)}"
        )


@router.get("/{client_id}", response_model=ReferenceClientResponse)
async def get_reference_client(
    client_id: int,
    db: AsyncSession = Depends(get_db),
    _: str = RequireAuth
) -> ReferenceClientResponse:
    """
    Get a specific reference client by ID.
    
    Args:
        client_id: Reference client ID
        db: Database session
        _: Authentication dependency
        
    Returns:
        Reference client data
        
    Raises:
        HTTPException: If client not found (404)
    """
    try:
        result = await db.execute(select(ReferenceClient).where(ReferenceClient.id == client_id))
        client = result.scalar_one_or_none()
        
        if not client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Reference client not found"
            )
        
        return ReferenceClientResponse.model_validate(client)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch reference client: {str(e)}"
        )


@router.put("/{client_id}", response_model=ReferenceClientResponse)
async def update_reference_client(
    client_id: int,
    client_data: ReferenceClientUpdate,
    db: AsyncSession = Depends(get_db),
    _: str = RequireAuth
) -> ReferenceClientResponse:
    """
    Update a reference client.
    
    Args:
        client_id: Reference client ID
        client_data: Updated client data
        db: Database session
        _: Authentication dependency
        
    Returns:
        Updated reference client
        
    Raises:
        HTTPException: If client not found (404)
    """
    try:
        result = await db.execute(select(ReferenceClient).where(ReferenceClient.id == client_id))
        client = result.scalar_one_or_none()
        
        if not client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Reference client not found"
            )
        
        # Update only provided fields
        update_data = client_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(client, field, value)
        
        await db.commit()
        await db.refresh(client)
        
        return ReferenceClientResponse.model_validate(client)
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update reference client: {str(e)}"
        )


@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_reference_client(
    client_id: int,
    db: AsyncSession = Depends(get_db),
    _: str = RequireAuth
) -> None:
    """
    Delete a reference client.
    
    Args:
        client_id: Reference client ID
        db: Database session
        _: Authentication dependency
        
    Raises:
        HTTPException: If client not found (404)
    """
    try:
        result = await db.execute(select(ReferenceClient).where(ReferenceClient.id == client_id))
        client = result.scalar_one_or_none()
        
        if not client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Reference client not found"
            )
        
        await db.delete(client)
        await db.commit()
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete reference client: {str(e)}"
        )