"""
Database initialization script (creates all tables without migrations)
Run this instead of alembic if you have migration issues
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.core.database import Base, engine_sync
from app.models import User, Store, Product, PriceChangeLog, CompetitorPrice, SimulationResult

def init_db():
    """Create all tables"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine_sync)
    print("✓ All tables created successfully!")
    print("\nTables created:")
    for table in Base.metadata.tables:
        print(f"  - {table}")

if __name__ == "__main__":
    init_db()
