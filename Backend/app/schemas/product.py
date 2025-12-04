from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ProductBase(BaseModel):
    sku: str
    title: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    cost_price: float
    current_price: float
    min_price: float
    max_price: float
    inventory: int = 0
    stock_age_days: int = 0
    metadata: dict = {}


class ProductCreate(ProductBase):
    store_id: int
    predicted_price: Optional[float] = None


class ProductUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    inventory: Optional[int] = None
    cost_price: Optional[float] = None
    current_price: Optional[float] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    predicted_price: Optional[float] = None
    stock_age_days: Optional[int] = None
    metadata: Optional[dict] = None


class Product(ProductBase):
    id: int
    store_id: int
    predicted_price: Optional[float] = None
    last_price_change: Optional[datetime] = None
    cooldown_seconds: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class PriceRecommendationRequest(BaseModel):
    product_id: Optional[int] = None
    features: Optional[dict] = None


class PriceRecommendation(BaseModel):
    new_price: float
    confidence: float
    reason: str
    predicted_revenue_change: float
    stockout_prediction: float


class AutoPricingRequest(BaseModel):
    store_id: int
    enabled: bool


class SimulationRequest(BaseModel):
    store_id: int
    days: int = 30
    strategy: str = "revenue_maximize"


class SimulationResponse(BaseModel):
    simulation_id: int
    store_id: int
    predicted_revenue_change: float
    csv_download_url: str
