"""
Background tasks using FastAPI BackgroundTasks (no Celery/Redis needed)
For production, consider using a proper task queue or scheduled jobs
"""
import random
from datetime import datetime, timedelta
from typing import List
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.models.product import Product
from app.models.price_change_log import PriceChangeLog
from app.models.competitor_price import CompetitorPrice
from app.models.simulation_result import SimulationResult
from app.ml.inference import get_model

# Synchronous DB session for background tasks
engine = create_engine(settings.DATABASE_URL_SYNC)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def run_price_update(product_id: int):
    """
    Background task to recalculate and update product price
    """
    db = SessionLocal()
    
    try:
        # Get product
        product = db.query(Product).filter(Product.id == product_id).first()
        
        if not product:
            return {"error": f"Product {product_id} not found"}
        
        # Get competitor average
        cutoff_time = datetime.utcnow() - timedelta(hours=24)
        competitor_prices = db.query(CompetitorPrice).filter(
            CompetitorPrice.product_id == product_id,
            CompetitorPrice.timestamp >= cutoff_time
        ).all()
        
        competitor_avg = None
        if competitor_prices:
            competitor_avg = sum(cp.price for cp in competitor_prices) / len(competitor_prices)
        
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
        
        # Get price prediction
        model = get_model()
        prediction = model.predict_price(features)
        new_price = prediction["new_price"]
        
        # Check cooldown
        if product.last_price_change:
            time_since_last = datetime.utcnow() - product.last_price_change
            if time_since_last.total_seconds() < product.cooldown_seconds:
                return {"message": "Cooldown active, skipping update"}
        
        # Check min/max bounds
        if new_price < product.min_price or new_price > product.max_price:
            new_price = max(product.min_price, min(product.max_price, new_price))
        
        # Check if price actually changed
        if abs(new_price - product.current_price) < 0.01:
            return {"message": "No significant price change needed"}
        
        # Log price change
        log = PriceChangeLog(
            product_id=product_id,
            old_price=product.current_price,
            new_price=new_price,
            reason=prediction["reason"],
            confidence=prediction["confidence"]
        )
        db.add(log)
        
        # Update product price
        product.current_price = new_price
        product.last_price_change = datetime.utcnow()
        
        db.commit()
        
        return {
            "product_id": product_id,
            "old_price": log.old_price,
            "new_price": new_price,
            "reason": prediction["reason"]
        }
        
    except Exception as e:
        db.rollback()
        print(f"Error in run_price_update: {e}")
        return {"error": str(e)}
    finally:
        db.close()


def run_scraper(product_ids: List[int] = None):
    """
    Background task to scrape competitor prices
    This is a mock implementation - replace with actual scraping logic
    """
    db = SessionLocal()
    
    try:
        if not product_ids:
            # Get all products
            products = db.query(Product).limit(100).all()
            product_ids = [p.id for p in products]
        
        scraped_count = 0
        
        for product_id in product_ids:
            # Mock scraping - replace with actual HTTP requests
            competitors = ["Amazon", "Walmart", "Target"]
            
            for competitor in competitors:
                # Simulate scraped price
                mock_price = random.uniform(10.0, 100.0)
                
                competitor_price = CompetitorPrice(
                    product_id=product_id,
                    competitor_name=competitor,
                    price=round(mock_price, 2),
                    timestamp=datetime.utcnow()
                )
                db.add(competitor_price)
                scraped_count += 1
        
        db.commit()
        
        return {
            "message": f"Scraped {scraped_count} competitor prices",
            "products_processed": len(product_ids)
        }
        
    except Exception as e:
        db.rollback()
        print(f"Error in run_scraper: {e}")
        return {"error": str(e)}
    finally:
        db.close()


def run_simulation(store_id: int, days: int = 30, strategy: str = "revenue_maximize"):
    """
    Background task to run pricing simulation/backtest
    This is a mock implementation - replace with actual simulation logic
    """
    db = SessionLocal()
    
    try:
        # Get all products for the store
        products = db.query(Product).filter(Product.store_id == store_id).all()
        
        if not products:
            return {"error": f"No products found for store {store_id}"}
        
        # Mock simulation
        total_revenue_change = 0.0
        
        for product in products:
            # Simulate price changes over the period
            daily_revenue_change = random.uniform(-2.0, 8.0)
            total_revenue_change += daily_revenue_change
        
        avg_revenue_change = total_revenue_change / len(products)
        
        # Store simulation result
        period_start = datetime.utcnow() - timedelta(days=days)
        period_end = datetime.utcnow()
        
        simulation = SimulationResult(
            store_id=store_id,
            period_start=period_start,
            period_end=period_end,
            predicted_revenue_change=round(avg_revenue_change, 2),
            strategy=strategy,
            csv_path=f"simulations/store_{store_id}_{datetime.utcnow().timestamp()}.csv"
        )
        
        db.add(simulation)
        db.commit()
        db.refresh(simulation)
        
        return {
            "simulation_id": simulation.id,
            "store_id": store_id,
            "predicted_revenue_change": simulation.predicted_revenue_change,
            "products_analyzed": len(products)
        }
        
    except Exception as e:
        db.rollback()
        print(f"Error in run_simulation: {e}")
        return {"error": str(e)}
    finally:
        db.close()
