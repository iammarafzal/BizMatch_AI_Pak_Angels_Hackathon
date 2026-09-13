from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.core.database import get_db
from app.models.manager import Manager
from app.schemas.manager import ManagerResponse

router = APIRouter(prefix="/managers", tags=["Managers"])

ID_ALIASES = {
    "mgr_01": "mgr-sarah-khan",
    "mgr-sarah-khan": "mgr_01",
    "mgr_02": "mgr-maria-james",
    "mgr-maria-james": "mgr_02",
    "mgr_03": "mgr-ali-ahmed",
    "mgr-ali-ahmed": "mgr_03",
}

@router.get("", response_model=List[ManagerResponse], include_in_schema=False)
@router.get("/", response_model=List[ManagerResponse])
def get_managers(
    limit: Optional[int] = Query(20, ge=1, le=100, description="Maximum number of managers to retrieve"),
    db: Session = Depends(get_db)
):
    """
    Retrieve curated manager profiles directly from the SQLite database.
    """
    query = select(Manager).limit(limit)
    result = db.execute(query)
    return result.scalars().all()

@router.get("/{manager_id}", response_model=ManagerResponse)
def get_manager_by_id(
    manager_id: str,
    db: Session = Depends(get_db)
):
    """
    Retrieve details for a single manager candidate by ID.
    Supports canonical IDs (e.g. 'mgr_01') and slug aliases (e.g. 'mgr-sarah-khan').
    """
    lookup_ids = [manager_id]
    alias = ID_ALIASES.get(manager_id)
    if alias:
        lookup_ids.append(alias)

    result = db.execute(select(Manager).filter(Manager.id.in_(lookup_ids)))
    manager = result.scalars().first()
    if not manager:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Manager with ID '{manager_id}' not found"
        )
    return manager
