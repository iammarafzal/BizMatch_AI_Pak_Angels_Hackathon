from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.database import get_db
from app.models.manager import Manager
from app.schemas.manager import ManagerResponse

router = APIRouter(prefix="/managers", tags=["Managers"])

@router.get("/", response_model=List[ManagerResponse])
async def get_managers(
    limit: Optional[int] = Query(20, ge=1, le=100, description="Maximum number of managers to retrieve"),
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve curated manager profiles.
    """
    query = select(Manager).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/{manager_id}", response_model=ManagerResponse)
async def get_manager_by_id(
    manager_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve details for a single manager candidate by ID.
    """
    result = await db.execute(select(Manager).filter(Manager.id == manager_id))
    manager = result.scalars().first()
    if not manager:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Manager with ID '{manager_id}' not found"
        )
    return manager
