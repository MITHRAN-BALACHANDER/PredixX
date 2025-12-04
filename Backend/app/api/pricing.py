from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.security import get_current_user, get_current_active_admin
from app.models.user import User
from app.models.product import Product
from app.models.store import Store
from app.schemas.product import (
    PriceRecommendationRequest,
    PriceRecommendation,
    AutoPricingRequest,
    SimulationRequest,
    SimulationResponse
)
from app.ml.inference import get_model
from app.services.pricing_rules import PricingRules
from app.workers import background_tasks

router = APIRouter(prefix="/price", tags=["pricing"])


@router.post("/recommend", response_model=PriceRecommendation)
async def recommend_price(
    request: PriceRecommendationRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get price recommendation for a product"""
    
    if request.product_id:
        # Get product from DB
        result = await db.execute(select(Product).where(Product.id == request.product_id))
        product = result.scalar_one_or_none()
        
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        
        # Get competitor average price
        competitor_avg = await PricingRules.get_competitor_avg_price(product.id, db)
        
        # Build features
        features = {
            "current_price": product.current_price,
            "cost_price": product.cost_price,
            "inventory": product.inventory,
            "stock_age_days": product.stock_age_days,
            "competitor_avg_price": competitor_avg,
            "min_price": product.min_price,
            "max_price": product.max_price,
            "strategy": "revenue_maximize"
        }
    elif request.features:
        features = request.features
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Must provide either product_id or features"
        )
    
    # Get model prediction
    model = get_model()
    prediction = model.predict_price(features)
    
    return prediction


@router.post("/auto", status_code=status.HTTP_200_OK)
async def toggle_auto_pricing(
    request: AutoPricingRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_admin)
):
    """Enable/disable auto-pricing for a store (admin only)"""
    
    result = await db.execute(select(Store).where(Store.id == request.store_id))
    store = result.scalar_one_or_none()
    
    if not store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Store not found"
        )
    
    store.auto_pricing_enabled = 1 if request.enabled else 0
    await db.commit()
    
    return {
        "message": f"Auto-pricing {'enabled' if request.enabled else 'disabled'} for store {store.name}",
        "store_id": store.id,
        "auto_pricing_enabled": request.enabled
    }


@router.post("/simulate", response_model=SimulationResponse)
async def simulate_pricing(
    request: SimulationRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Run a pricing simulation/backtest for a store"""
    
    result = await db.execute(select(Store).where(Store.id == request.store_id))
    store = result.scalar_one_or_none()
    
    if not store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Store not found"
        )
    
    # Queue simulation task
    from app.workers import background_tasks as bt
    background_tasks.add_task(
        bt.run_simulation,
        request.store_id,
        request.days,
        request.strategy
    )
    
    # For now, return a mock response
    # In production, you'd track the task and return results when ready
    return {
        "simulation_id": 1,  # Would be actual simulation result ID
        "store_id": request.store_id,
        "predicted_revenue_change": 12.5,  # Mock value
        "csv_download_url": f"/api/v1/simulations/1/download"
    }
