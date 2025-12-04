from sqlalchemy import Column, Integer, Float, ForeignKey, DateTime, String
from sqlalchemy.sql import func
from app.core.database import Base


class SimulationResult(Base):
    __tablename__ = "simulation_results"
    
    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(Integer, ForeignKey("stores.id"), nullable=False)
    period_start = Column(DateTime(timezone=True), nullable=False)
    period_end = Column(DateTime(timezone=True), nullable=False)
    predicted_revenue_change = Column(Float, nullable=False)
    strategy = Column(String, nullable=True)
    csv_path = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
