from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, JSON, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(Integer, ForeignKey("stores.id"), nullable=False)
    sku = Column(String, index=True, nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)  # Product description for ML
    image_url = Column(String, nullable=True)  # Product image URL
    cost_price = Column(Float, nullable=False)
    current_price = Column(Float, nullable=False)
    min_price = Column(Float, nullable=False)
    max_price = Column(Float, nullable=False)
    predicted_price = Column(Float, nullable=True)  # ML predicted price
    inventory = Column(Integer, default=0)
    stock_age_days = Column(Integer, default=0)
    product_metadata = Column(JSON, default=dict)  # Renamed from 'metadata' to avoid conflict
    last_price_change = Column(DateTime(timezone=True), nullable=True)
    cooldown_seconds = Column(Integer, default=3600)  # 1 hour default
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    store = relationship("Store", back_populates="products")
    price_logs = relationship("PriceChangeLog", back_populates="product")
    competitor_prices = relationship("CompetitorPrice", back_populates="product")
