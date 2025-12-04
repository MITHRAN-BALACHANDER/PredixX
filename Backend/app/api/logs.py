from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.price_change_log import PriceChangeLog
from app.schemas.webhook import PriceChangeLog as PriceChangeLogSchema

router = APIRouter(prefix="/logs", tags=["logs"])


@router.get("/price-changes", response_model=List[PriceChangeLogSchema])
async def get_price_change_logs(
    product_id: int = Query(None),
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get price change logs with pagination"""
    
    query = select(PriceChangeLog).order_by(PriceChangeLog.created_at.desc())
    
    if product_id:
        query = query.where(PriceChangeLog.product_id == product_id)
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    logs = result.scalars().all()
    
    return logs
