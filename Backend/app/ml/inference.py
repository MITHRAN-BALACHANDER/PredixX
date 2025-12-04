"""
ML Model Inference with Real Model Integration
Integrates with trained models from amazon_price_model/artifacts
"""
import os
import random
import joblib
import numpy as np
from typing import Dict, Any, Optional
from datetime import datetime
from app.core.config import settings


class PriceModel:
    def __init__(self, model_path: str = None):
        self.model_path = model_path
        self.model_text = None
        self.model_image = None
        self.tfidf = None
        self.text_feature_cols = None
        self.image_quality_data = None
        self.use_real_models = False
        
        # Load models if available
        self.load_models()
    
    def load_models(self):
        """Load the actual models from disk"""
        models_dir = settings.MODELS_DIR  # Use path from config
        
        try:
            # Check if model files exist
            text_model_path = os.path.join(models_dir, "model_text_v5.pkl")
            image_model_path = os.path.join(models_dir, "model_image_v5.pkl")
            tfidf_path = os.path.join(models_dir, "tfidf_text_v5.pkl")
            text_cols_path = os.path.join(models_dir, "text_feature_cols_v5.pkl")
            image_quality_path = os.path.join(models_dir, "image_quality_train_v5.npy")
            
            if os.path.exists(text_model_path):
                print(f"Loading text model from {text_model_path}")
                self.model_text = joblib.load(text_model_path)
                print("✓ Text model loaded successfully")
            
            if os.path.exists(image_model_path):
                print(f"Loading image model from {image_model_path}")
                self.model_image = joblib.load(image_model_path)
                print("✓ Image model loaded successfully")
            
            if os.path.exists(tfidf_path):
                self.tfidf = joblib.load(tfidf_path)
                print("✓ TF-IDF vectorizer loaded successfully")
            
            if os.path.exists(text_cols_path):
                self.text_feature_cols = joblib.load(text_cols_path)
                print("✓ Text feature columns loaded successfully")
            
            if os.path.exists(image_quality_path):
                self.image_quality_data = np.load(image_quality_path)
                print(f"✓ Image quality data loaded successfully (shape: {self.image_quality_data.shape})")
            
            # Check if we can use real models
            if self.model_text is not None or self.model_image is not None:
                self.use_real_models = True
                print("✓ Real models are available and will be used for predictions")
            else:
                print("⚠ No models found, using fallback stub predictions")
                
        except Exception as e:
            print(f"⚠ Error loading models: {e}")
            print("⚠ Falling back to stub predictions")
            self.use_real_models = False
    
    def predict_with_real_model(self, features: Dict[str, Any]) -> Optional[float]:
        """
        Use the real trained model for prediction
        
        Args:
            features: Product features dictionary
            
        Returns:
            Predicted price or None if model can't make prediction
        """
        try:
            # Extract product title for text model
            title = features.get("title", "")
            
            # Vectorize text and predict
            if self.tfidf and self.model_text and title:
                # Transform title using TF-IDF
                text_features = self.tfidf.transform([title])
                
                # Predict price
                text_prediction = self.model_text.predict(text_features)[0]
                
                # If we also had image features and model, we could combine them
                # For now, we'll rely on the text model if available
                
                return float(text_prediction)
            
            return None
            
        except Exception as e:
            print(f"⚠ Error in real model prediction: {e}")
            return None
    
    def predict_price(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predict optimal price for a product
        
        Args:
            features: Dictionary containing:
                - current_price: float
                - cost_price: float
                - inventory: int
                - stock_age_days: int
                - competitor_avg_price: float (optional)
                - sales_velocity: float (optional)
                - margin_target: float (optional)
                - strategy: str (revenue_maximize, clearance, competitive)
                - title: str (optional, for text model)
                - image_features: dict (optional, for image model)
        
        Returns:
            Dictionary with prediction results:
                - new_price: float
                - confidence: float (0-1)
                - reason: str
                - predicted_revenue_change: float (percentage)
                - stockout_prediction: float (0-1 probability)
                - model_used: str (real_model or rule_based)
        """
        
        # Extract features
        current_price = features.get("current_price", 0)
        cost_price = features.get("cost_price", 0)
        inventory = features.get("inventory", 0)
        stock_age_days = features.get("stock_age_days", 0)
        competitor_avg_price = features.get("competitor_avg_price")
        strategy = features.get("strategy", "revenue_maximize")
        min_price = features.get("min_price", cost_price * 1.1)
        max_price = features.get("max_price", cost_price * 3.0)
        
        # Try to use real model first
        real_prediction = None
        if self.use_real_models:
            real_prediction = self.predict_with_real_model(features)
        
        # If real model provided a prediction, use it as a base
        if real_prediction is not None:
            new_price = real_prediction
            reason = "ML Model prediction"
            confidence = 0.92
            model_used = "real_model"
        else:
            # Fall back to rule-based prediction
            new_price, reason, confidence = self._rule_based_prediction(
                current_price, cost_price, inventory, stock_age_days,
                competitor_avg_price, strategy, min_price, max_price
            )
            model_used = "rule_based"
        
        # Ensure price is within bounds
        new_price = max(min_price, min(max_price, new_price))
        new_price = round(new_price, 2)
        
        # Stockout prediction (simplified)
        if inventory < 5:
            stockout_prediction = 0.8
        elif inventory < 20:
            stockout_prediction = 0.3
        else:
            stockout_prediction = 0.05
        
        return {
            "new_price": new_price,
            "confidence": round(confidence, 2),
            "reason": reason,
            "predicted_revenue_change": round(random.uniform(-2.0, 8.0), 2),
            "stockout_prediction": round(stockout_prediction, 2),
            "model_used": model_used
        }
    
    def _rule_based_prediction(
        self, 
        current_price: float,
        cost_price: float,
        inventory: int,
        stock_age_days: int,
        competitor_avg_price: Optional[float],
        strategy: str,
        min_price: float,
        max_price: float
    ) -> tuple[float, str, float]:
        """
        Rule-based prediction logic
        
        Returns:
            (new_price, reason, confidence)
        """
        
        if strategy == "clearance":
            # Aggressive pricing for old stock
            if stock_age_days > 90:
                new_price = max(min_price, current_price * 0.7)
                reason = "Clearance strategy: High stock age"
            elif stock_age_days > 60:
                new_price = max(min_price, current_price * 0.85)
                reason = "Clearance strategy: Moderate stock age"
            else:
                new_price = max(min_price, current_price * 0.95)
                reason = "Clearance strategy: Low stock age"
            confidence = 0.85
            predicted_revenue_change = -15.0  # May reduce revenue but clear stock
            
        elif strategy == "competitive":
            # Price based on competition
            if competitor_avg_price:
                new_price = competitor_avg_price * 0.98  # Slightly undercut
                reason = "Competitive strategy: Undercutting competitors"
                confidence = 0.80
                predicted_revenue_change = 5.0
            else:
                new_price = current_price
                reason = "No competitor data available"
                confidence = 0.5
                predicted_revenue_change = 0.0
                
        else:  # revenue_maximize
            # Dynamic pricing based on inventory and demand signals
            if inventory < 10:
                # Low inventory, increase price
                new_price = min(max_price, current_price * 1.08)
                reason = "Revenue maximization: Low inventory"
                confidence = 0.90
                predicted_revenue_change = 8.0
            elif inventory > 100:
                # High inventory, decrease price to move stock
                new_price = max(min_price, current_price * 0.95)
                reason = "Revenue maximization: High inventory"
                confidence = 0.85
                predicted_revenue_change = 3.0
            else:
                # Optimal inventory level
                new_price = current_price * random.uniform(0.98, 1.02)
                reason = "Revenue maximization: Optimal inventory"
                confidence = 0.75
        
        return new_price, reason, confidence


# Global model instance
_model = None


def get_model() -> PriceModel:
    """Get or create the global model instance"""
    global _model
    if _model is None:
        from app.core.config import settings
        _model = PriceModel(model_path=settings.MODEL_PATH)
    return _model
