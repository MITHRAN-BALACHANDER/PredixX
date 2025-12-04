from pydantic import BaseModel
from datetime import datetime


class InventoryWebhook(BaseModel):
    product_id: int
    inventory: int
    stock_age_days: int = 0


class CompetitorPriceWebhook(BaseModel):
    product_id: int
    competitor_name: str
    price: float


class PriceChangeLog(BaseModel):
    id: int
    product_id: int
    old_price: float
    new_price: float
    reason: str
    confidence: float
    created_at: datetime
    
    class Config:
        from_attributes = True
