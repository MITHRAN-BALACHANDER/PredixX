from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional

from app.core.database import get_db
from app.core.security import get_current_user, get_current_active_admin
from app.models.user import User
from app.models.store import Store
from app.schemas.store import Store as StoreSchema, StoreCreate, StoreUpdate

router = APIRouter(prefix="/stores", tags=["stores"])


@router.get("", response_model=List[StoreSchema])
async def list_stores(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List stores"""
    query = select(Store).offset(skip).limit(limit)
    
    # If not admin, only show own stores
    if current_user.role != "admin":
        query = query.where(Store.owner_id == current_user.id)
        
    result = await db.execute(query)
    stores = result.scalars().all()
    
    return stores


@router.post("", response_model=StoreSchema, status_code=status.HTTP_201_CREATED)
async def create_store(
    store_data: StoreCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new store"""
    
    # Check if API key already exists
    result = await db.execute(select(Store).where(Store.api_key == store_data.api_key))
    existing_store = result.scalar_one_or_none()
    
    if existing_store:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="API key already registered"
        )
    
    store = Store(
        **store_data.model_dump(),
        owner_id=current_user.id
    )
    
    db.add(store)
    await db.commit()
    await db.refresh(store)
    
    return store


@router.get("/{store_id}", response_model=StoreSchema)
async def get_store(
    store_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a store by ID"""
    result = await db.execute(select(Store).where(Store.id == store_id))
    store = result.scalar_one_or_none()
    
    if not store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Store not found"
        )
    
    # Check permissions
    if current_user.role != "admin" and store.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this store"
        )
    
    return store


@router.patch("/{store_id}", response_model=StoreSchema)
async def update_store(
    store_id: int,
    store_data: StoreUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a store"""
    result = await db.execute(select(Store).where(Store.id == store_id))
    store = result.scalar_one_or_none()
    
    if not store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Store not found"
        )
    
    # Check permissions
    if current_user.role != "admin" and store.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this store"
        )
    
    # Update fields
    update_data = store_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(store, field, value)
    
    await db.commit()
    await db.refresh(store)
    
    return store


@router.delete("/{store_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_store(
    store_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a store"""
    result = await db.execute(select(Store).where(Store.id == store_id))
    store = result.scalar_one_or_none()
    
    if not store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Store not found"
        )
    
    # Check permissions
    if current_user.role != "admin" and store.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this store"
        )
    
    await db.delete(store)
    await db.commit()
    
    return None
