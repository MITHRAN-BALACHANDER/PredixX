import asyncio
import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.api.stores import create_store, list_stores, get_store, update_store, delete_store
from app.api.products import delete_product, create_product
from app.schemas.store import StoreCreate, StoreUpdate
from app.schemas.product import ProductCreate
from app.models.user import User
from app.core.database import AsyncSessionLocal

# Mock user
mock_user = User(id=1, email="test@example.com", role="admin")

async def verify_api():
    print("=" * 60)
    print("API VERIFICATION")
    print("=" * 60)
    print()
    
    async with AsyncSessionLocal() as db:
        try:
            # 1. Test Store Creation
            print("1. Testing Store Creation...")
            store_data = StoreCreate(name="Test Store", api_key=f"test_key_{int(datetime.now().timestamp())}")
            store = await create_store(store_data, db, mock_user)
            print(f"✓ Store created: {store.name} (ID: {store.id})")
            
            # 2. Test Store Listing
            print("\n2. Testing Store Listing...")
            stores = await list_stores(0, 100, db, mock_user)
            print(f"✓ Found {len(stores)} stores")
            
            # 3. Test Store Get
            print("\n3. Testing Store Get...")
            fetched_store = await get_store(store.id, db, mock_user)
            print(f"✓ Fetched store: {fetched_store.name}")
            
            # 4. Test Store Update
            print("\n4. Testing Store Update...")
            update_data = StoreUpdate(name="Updated Store Name")
            updated_store = await update_store(store.id, update_data, db, mock_user)
            print(f"✓ Updated store name: {updated_store.name}")
            
            # 5. Test Product Creation (for delete test)
            print("\n5. Testing Product Creation...")
            product_data = ProductCreate(
                store_id=store.id,
                sku=f"SKU-{int(datetime.now().timestamp())}",
                name="Test Product",
                current_price=100.0,
                cost_price=50.0,
                inventory=10,
                min_price=80.0,
                max_price=150.0
            )
            product = await create_product(product_data, db, mock_user)
            print(f"✓ Product created: {product.name} (ID: {product.id})")
            
            # 6. Test Product Delete
            print("\n6. Testing Product Delete...")
            await delete_product(product.id, db, mock_user)
            print("✓ Product deleted")
            
            # 7. Test Store Delete
            print("\n7. Testing Store Delete...")
            await delete_store(store.id, db, mock_user)
            print("✓ Store deleted")
            
            print("\n" + "=" * 60)
            print("✓ ALL API TESTS PASSED")
            print("=" * 60)
            
        except Exception as e:
            print(f"\n❌ API TEST FAILED: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    # Run async test
    asyncio.run(verify_api())
