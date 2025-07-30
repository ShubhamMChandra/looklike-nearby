"""
Campaigns API routes for organizing prospects into outreach campaigns.

WHAT: Provides FastAPI routes for CRUD operations on campaigns and
      campaign-prospect associations for organizing lead generation efforts.

WHY: Sales teams need to organize prospects into named campaigns
     (e.g., "Q1 2025 Chicago") and track their outreach status through
     the sales funnel.

HOW: Uses FastAPI routers with async database operations, status tracking,
     and Pydantic models for request/response validation.

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
from sqlalchemy.orm import selectinload

from backend.auth.password_auth import RequireAuth
from backend.database.config import get_db
from backend.models.campaign import Campaign, CampaignProspect, ProspectStatus

router = APIRouter()


class CampaignCreate(BaseModel):
    """Request model for creating campaigns."""
    name: str
    description: Optional[str] = None


class CampaignUpdate(BaseModel):
    """Request model for updating campaigns."""
    name: Optional[str] = None
    description: Optional[str] = None


class CampaignResponse(BaseModel):
    """Response model for campaign data."""
    id: int
    name: str
    description: Optional[str]
    prospect_count: int = 0
    contacted_count: int = 0
    qualified_count: int = 0
    converted_count: int = 0
    
    class Config:
        from_attributes = True


class CampaignsListResponse(BaseModel):
    """Response model for campaigns list."""
    campaigns: List[CampaignResponse]
    total: int


class AddProspectToCampaignRequest(BaseModel):
    """Request model for adding prospects to campaigns."""
    prospect_place_id: str
    reference_client_id: Optional[int] = None
    notes: Optional[str] = None


class UpdateProspectStatusRequest(BaseModel):
    """Request model for updating prospect status."""
    status: ProspectStatus
    notes: Optional[str] = None


@router.get("", response_model=CampaignsListResponse)
async def get_campaigns(
    db: AsyncSession = Depends(get_db),
    _: str = RequireAuth
) -> CampaignsListResponse:
    """
    Get all campaigns with prospect counts.
    
    Args:
        db: Database session
        _: Authentication dependency
        
    Returns:
        List of all campaigns with statistics
    """
    try:
        # Get campaigns with their prospects
        result = await db.execute(
            select(Campaign).options(selectinload(Campaign.campaign_prospects))
        )
        campaigns = result.scalars().all()
        
        campaign_responses = []
        for campaign in campaigns:
            # Calculate status counts
            prospects = campaign.campaign_prospects
            prospect_count = len(prospects)
            contacted_count = len([p for p in prospects if p.status == ProspectStatus.CONTACTED])
            qualified_count = len([p for p in prospects if p.status == ProspectStatus.QUALIFIED])
            converted_count = len([p for p in prospects if p.status == ProspectStatus.CONVERTED])
            
            campaign_responses.append(CampaignResponse(
                id=campaign.id,
                name=campaign.name,
                description=campaign.description,
                prospect_count=prospect_count,
                contacted_count=contacted_count,
                qualified_count=qualified_count,
                converted_count=converted_count
            ))
        
        return CampaignsListResponse(
            campaigns=campaign_responses,
            total=len(campaign_responses)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch campaigns: {str(e)}"
        )


@router.post("", response_model=CampaignResponse, status_code=status.HTTP_201_CREATED)
async def create_campaign(
    campaign_data: CampaignCreate,
    db: AsyncSession = Depends(get_db),
    _: str = RequireAuth
) -> CampaignResponse:
    """
    Create a new campaign.
    
    Args:
        campaign_data: Campaign data
        db: Database session
        _: Authentication dependency
        
    Returns:
        Created campaign
    """
    try:
        # Create new campaign
        campaign = Campaign(**campaign_data.model_dump())
        db.add(campaign)
        await db.commit()
        await db.refresh(campaign)
        
        return CampaignResponse(
            id=campaign.id,
            name=campaign.name,
            description=campaign.description,
            prospect_count=0,
            contacted_count=0,
            qualified_count=0,
            converted_count=0
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create campaign: {str(e)}"
        )


@router.get("/{campaign_id}", response_model=CampaignResponse)
async def get_campaign(
    campaign_id: int,
    db: AsyncSession = Depends(get_db),
    _: str = RequireAuth
) -> CampaignResponse:
    """
    Get a specific campaign by ID.
    
    Args:
        campaign_id: Campaign ID
        db: Database session
        _: Authentication dependency
        
    Returns:
        Campaign data with statistics
        
    Raises:
        HTTPException: If campaign not found (404)
    """
    try:
        result = await db.execute(
            select(Campaign)
            .options(selectinload(Campaign.campaign_prospects))
            .where(Campaign.id == campaign_id)
        )
        campaign = result.scalar_one_or_none()
        
        if not campaign:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campaign not found"
            )
        
        # Calculate status counts
        prospects = campaign.campaign_prospects
        prospect_count = len(prospects)
        contacted_count = len([p for p in prospects if p.status == ProspectStatus.CONTACTED])
        qualified_count = len([p for p in prospects if p.status == ProspectStatus.QUALIFIED])
        converted_count = len([p for p in prospects if p.status == ProspectStatus.CONVERTED])
        
        return CampaignResponse(
            id=campaign.id,
            name=campaign.name,
            description=campaign.description,
            prospect_count=prospect_count,
            contacted_count=contacted_count,
            qualified_count=qualified_count,
            converted_count=converted_count
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch campaign: {str(e)}"
        )


@router.put("/{campaign_id}", response_model=CampaignResponse)
async def update_campaign(
    campaign_id: int,
    campaign_data: CampaignUpdate,
    db: AsyncSession = Depends(get_db),
    _: str = RequireAuth
) -> CampaignResponse:
    """
    Update a campaign.
    
    Args:
        campaign_id: Campaign ID
        campaign_data: Updated campaign data
        db: Database session
        _: Authentication dependency
        
    Returns:
        Updated campaign
        
    Raises:
        HTTPException: If campaign not found (404)
    """
    try:
        result = await db.execute(
            select(Campaign)
            .options(selectinload(Campaign.campaign_prospects))
            .where(Campaign.id == campaign_id)
        )
        campaign = result.scalar_one_or_none()
        
        if not campaign:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campaign not found"
            )
        
        # Update only provided fields
        update_data = campaign_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(campaign, field, value)
        
        await db.commit()
        await db.refresh(campaign)
        
        # Calculate status counts
        prospects = campaign.campaign_prospects
        prospect_count = len(prospects)
        contacted_count = len([p for p in prospects if p.status == ProspectStatus.CONTACTED])
        qualified_count = len([p for p in prospects if p.status == ProspectStatus.QUALIFIED])
        converted_count = len([p for p in prospects if p.status == ProspectStatus.CONVERTED])
        
        return CampaignResponse(
            id=campaign.id,
            name=campaign.name,
            description=campaign.description,
            prospect_count=prospect_count,
            contacted_count=contacted_count,
            qualified_count=qualified_count,
            converted_count=converted_count
        )
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update campaign: {str(e)}"
        )


@router.delete("/{campaign_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_campaign(
    campaign_id: int,
    db: AsyncSession = Depends(get_db),
    _: str = RequireAuth
) -> None:
    """
    Delete a campaign.
    
    Args:
        campaign_id: Campaign ID
        db: Database session
        _: Authentication dependency
        
    Raises:
        HTTPException: If campaign not found (404)
    """
    try:
        result = await db.execute(select(Campaign).where(Campaign.id == campaign_id))
        campaign = result.scalar_one_or_none()
        
        if not campaign:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campaign not found"
            )
        
        await db.delete(campaign)
        await db.commit()
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete campaign: {str(e)}"
        )