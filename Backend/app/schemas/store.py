from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class StoreBase(BaseModel):
    name: str
    api_key: str
    auto_pricing_enabled: Optional[int] = 0

class StoreCreate(StoreBase):
    pass

class StoreUpdate(BaseModel):
    name: Optional[str] = None
    auto_pricing_enabled: Optional[int] = None

class Store(StoreBase):
    id: int
    owner_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
