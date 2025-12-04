"""
Business Rules Engine for Dynamic Pricing
"""
from datetime import datetime, timedelta
from typing import Dict, Tuple, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.product import Product
from app.models.competitor_price import CompetitorPrice


class PricingRules:
    """Business rules for price validation and adjustment"""
    
    MAX_PRICE_CHANGE_PCT = 0.15  # 15% max change
    
    @staticmethod
    async def validate_price_change(
        product: Product,
        new_price: float,
        db: AsyncSession
    ) -> Tuple[bool, Optional[str], Optional[float]]:
        """
        Validate if price change is allowed based on business rules
        
        Returns:
            (is_valid, error_message, adjusted_price)
        """
        
        # Rule 1: Respect min_price and max_price
        if new_price < product.min_price:
            return False, f"Price ${new_price} below minimum ${product.min_price}", product.min_price
        
        if new_price > product.max_price:
            return False, f"Price ${new_price} above maximum ${product.max_price}", product.max_price
        
        # Rule 2: Margin protection - never sell below cost + margin
        min_margin = 0.10  # 10% minimum margin
        min_price_with_margin = product.cost_price * (1 + min_margin)
        
        if new_price < min_price_with_margin:
            return False, f"Price ${new_price} violates margin protection (min: ${min_price_with_margin:.2f})", min_price_with_margin
        
        # Rule 3: Cooldown period check
        if product.last_price_change:
            time_since_last_change = datetime.utcnow() - product.last_price_change.replace(tzinfo=None)
            cooldown_delta = timedelta(seconds=product.cooldown_seconds)
            
            if time_since_last_change < cooldown_delta:
                remaining = cooldown_delta - time_since_last_change
                return False, f"Cooldown active. Wait {remaining.seconds} more seconds", None
        
        # Rule 4: Prevent large price swings (>15% unless manual override)
        price_change_pct = abs(new_price - product.current_price) / product.current_price
        
        if price_change_pct > PricingRules.MAX_PRICE_CHANGE_PCT:
            # Adjust to max allowed change
            if new_price > product.current_price:
                adjusted_price = product.current_price * (1 + PricingRules.MAX_PRICE_CHANGE_PCT)
            else:
                adjusted_price = product.current_price * (1 - PricingRules.MAX_PRICE_CHANGE_PCT)
            
            return True, f"Price change capped at {PricingRules.MAX_PRICE_CHANGE_PCT*100}%", round(adjusted_price, 2)
        
        return True, None, new_price
    
    @staticmethod
    async def get_competitor_avg_price(
        product_id: int,
        db: AsyncSession,
        window_hours: int = 24
    ) -> Optional[float]:
        """
        Get average competitor price with exponential smoothing
        Only consider prices from the last N hours
        """
        cutoff_time = datetime.utcnow() - timedelta(hours=window_hours)
        
        result = await db.execute(
            select(CompetitorPrice)
            .where(
                CompetitorPrice.product_id == product_id,
                CompetitorPrice.timestamp >= cutoff_time
            )
            .order_by(CompetitorPrice.timestamp.desc())
        )
        
        competitor_prices = result.scalars().all()
        
        if not competitor_prices:
            return None
        
        # Simple exponential smoothing
        alpha = 0.3  # Smoothing factor
        smoothed_price = competitor_prices[0].price
        
        for i in range(1, len(competitor_prices)):
            smoothed_price = alpha * competitor_prices[i].price + (1 - alpha) * smoothed_price
        
        return round(smoothed_price, 2)
    
    @staticmethod
    def apply_strategy_rules(
        strategy: str,
        base_features: Dict
    ) -> Dict:
        """
        Apply strategy-specific feature modifications
        
        Strategies:
        - revenue_maximize: Focus on profit optimization
        - clearance: Aggressive pricing to clear inventory
        - competitive: Match/undercut competitors
        """
        features = base_features.copy()
        features["strategy"] = strategy
        
        if strategy == "clearance":
            # More aggressive with old stock
            if features.get("stock_age_days", 0) > 60:
                features["margin_target"] = 0.05  # Accept lower margins
        
        elif strategy == "competitive":
            # Prioritize competitor pricing
            if "competitor_avg_price" not in features or features["competitor_avg_price"] is None:
                features["fallback_strategy"] = "revenue_maximize"
        
        return features
