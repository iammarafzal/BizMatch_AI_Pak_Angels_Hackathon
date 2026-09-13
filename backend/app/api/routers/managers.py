from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.core.database import get_db
from app.models.manager import Manager
from app.schemas.manager import ManagerResponse

router = APIRouter(prefix="/managers", tags=["Managers"])

@router.get("/", response_model=list[ManagerResponse])
async def get_managers(db: Session = Depends(get_db)):
    result = db.execute(select(Manager))
    return result.scalars().all()
