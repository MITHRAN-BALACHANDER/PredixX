import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_product(client: AsyncClient, auth_token, db_session):
    """Test product creation"""
    from app.models.store import Store
    
    # Create a store first
    store = Store(owner_id=1, name="Test Store", api_key="test-key-123")
    db_session.add(store)
    await db_session.commit()
    await db_session.refresh(store)
    
    response = await client.post(
        "/api/v1/products",
        json={
            "store_id": store.id,
            "sku": "TEST-SKU-001",
            "title": "Test Product",
            "cost_price": 10.0,
            "current_price": 20.0,
            "min_price": 12.0,
            "max_price": 30.0,
            "inventory": 100,
            "stock_age_days": 0
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["sku"] == "TEST-SKU-001"
    assert data["current_price"] == 20.0


@pytest.mark.asyncio
async def test_list_products(client: AsyncClient, auth_token, db_session):
    """Test listing products"""
    from app.models.store import Store
    from app.models.product import Product
    
    # Create store and products
    store = Store(owner_id=1, name="Test Store", api_key="test-key-123")
    db_session.add(store)
    await db_session.commit()
    await db_session.refresh(store)
    
    product = Product(
        store_id=store.id,
        sku="TEST-001",
        title="Product 1",
        cost_price=10.0,
        current_price=20.0,
        min_price=12.0,
        max_price=30.0,
        inventory=100
    )
    db_session.add(product)
    await db_session.commit()
    
    response = await client.get(
        "/api/v1/products",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[0]["sku"] == "TEST-001"


@pytest.mark.asyncio
async def test_update_product(client: AsyncClient, auth_token, db_session):
    """Test product update"""
    from app.models.store import Store
    from app.models.product import Product
    
    store = Store(owner_id=1, name="Test Store", api_key="test-key-123")
    db_session.add(store)
    await db_session.commit()
    await db_session.refresh(store)
    
    product = Product(
        store_id=store.id,
        sku="TEST-001",
        title="Product 1",
        cost_price=10.0,
        current_price=20.0,
        min_price=12.0,
        max_price=30.0,
        inventory=100
    )
    db_session.add(product)
    await db_session.commit()
    await db_session.refresh(product)
    
    response = await client.patch(
        f"/api/v1/products/{product.id}",
        json={"inventory": 50},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["inventory"] == 50
