"""
Model Verification Script
Run this to verify that models are properly loaded
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.ml.inference import get_model


def verify_models():
    print("=" * 60)
    print("MODEL VERIFICATION")
    print("=" * 60)
    print()
    
    # Get model instance
    model = get_model()
    
    print("Model Status:")
    print(f"  - Using real models: {model.use_real_models}")
    print(f"  - Text model loaded: {model.model_text is not None}")
    print(f"  - Image model loaded: {model.model_image is not None}")
    print(f"  - TF-IDF loaded: {model.tfidf is not None}")
    print(f"  - Text features loaded: {model.text_feature_cols is not None}")
    print(f"  - Image quality data loaded: {model.image_quality_data is not None}")
    print()
    
    # Test prediction
    print("Testing prediction with sample data...")
    test_features = {
        "current_price": 20.0,
        "cost_price": 10.0,
        "inventory": 50,
        "stock_age_days": 15,
        "min_price": 12.0,
        "max_price": 30.0,
        "strategy": "revenue_maximize"
    }
    
    result = model.predict_price(test_features)
    
    print("Prediction Result:")
    print(f"  - New Price: ${result['new_price']}")
    print(f"  - Confidence: {result['confidence']}")
    print(f"  - Reason: {result['reason']}")
    print(f"  - Model Used: {result.get('model_used', 'unknown')}")
    print(f"  - Revenue Change: {result['predicted_revenue_change']}%")
    print(f"  - Stockout Risk: {result['stockout_prediction']}")
    print()
    
    print("=" * 60)
    
    if model.use_real_models:
        print("✓ SUCCESS: Real models are loaded and ready!")
    else:
        print("⚠ WARNING: Using rule-based predictions (models not loaded)")
    
    print("=" * 60)


if __name__ == "__main__":
    verify_models()
