from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.database import get_db
from app.models.manager import Manager
from app.schemas.manager import ManagerResponse

router = APIRouter(prefix="/managers", tags=["Managers"])

@router.get("/", response_model=list[ManagerResponse])
async def get_managers(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Manager))
    return result.scalars().all()
