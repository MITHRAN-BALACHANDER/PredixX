from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime

from app.core.database import get_db
from app.models.product import Product
from app.models.competitor_price import CompetitorPrice
from app.schemas.webhook import InventoryWebhook, CompetitorPriceWebhook
from app.workers import background_tasks

router = APIRouter(prefix="/webhook", tags=["webhooks"])


@router.post("/inventory", status_code=status.HTTP_200_OK)
async def inventory_update(
    data: InventoryWebhook,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """Accept inventory updates from stores"""
    
    result = await db.execute(select(Product).where(Product.id == data.product_id))
    product = result.scalar_one_or_none()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Update inventory
    product.inventory = data.inventory
    product.stock_age_days = data.stock_age_days
    await db.commit()
    
    # Trigger price recalculation in background
    from app.workers import background_tasks as bt
    background_tasks.add_task(bt.run_price_update, data.product_id)
    
    return {
        "message": "Inventory updated successfully",
        "product_id": data.product_id,
        "inventory": data.inventory
    }


@router.post("/competitor", status_code=status.HTTP_201_CREATED)
async def competitor_price_update(
    data: CompetitorPriceWebhook,
    db: AsyncSession = Depends(get_db)
):
    """Accept competitor price updates"""
    
    result = await db.execute(select(Product).where(Product.id == data.product_id))
    product = result.scalar_one_or_none()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Store competitor price
    competitor_price = CompetitorPrice(
        product_id=data.product_id,
        competitor_name=data.competitor_name,
        price=data.price,
        timestamp=datetime.utcnow()
    )
    
    db.add(competitor_price)
    await db.commit()
    
    return {
        "message": "Competitor price stored successfully",
        "product_id": data.product_id,
        "competitor_name": data.competitor_name,
        "price": data.price
    }
