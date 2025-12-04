import pytest
from app.ml.inference import PriceModel


def test_predict_price_revenue_maximize():
    """Test price prediction with revenue_maximize strategy"""
    model = PriceModel()
    
    features = {
        "current_price": 20.0,
        "cost_price": 10.0,
        "inventory": 5,  # Low inventory
        "stock_age_days": 10,
        "min_price": 12.0,
        "max_price": 30.0,
        "strategy": "revenue_maximize"
    }
    
    result = model.predict_price(features)
    
    assert "new_price" in result
    assert "confidence" in result
    assert "reason" in result
    assert result["new_price"] >= features["min_price"]
    assert result["new_price"] <= features["max_price"]
    assert 0 <= result["confidence"] <= 1


def test_predict_price_clearance():
    """Test price prediction with clearance strategy"""
    model = PriceModel()
    
    features = {
        "current_price": 20.0,
        "cost_price": 10.0,
        "inventory": 100,
        "stock_age_days": 95,  # Old stock
        "min_price": 12.0,
        "max_price": 30.0,
        "strategy": "clearance"
    }
    
    result = model.predict_price(features)
    
    assert result["new_price"] < features["current_price"]
    assert "clearance" in result["reason"].lower()


def test_predict_price_competitive():
    """Test price prediction with competitive strategy"""
    model = PriceModel()
    
    features = {
        "current_price": 20.0,
        "cost_price": 10.0,
        "inventory": 50,
        "stock_age_days": 10,
        "competitor_avg_price": 19.0,
        "min_price": 12.0,
        "max_price": 30.0,
        "strategy": "competitive"
    }
    
    result = model.predict_price(features)
    
    assert result["new_price"] <= features["competitor_avg_price"]
    assert "competitive" in result["reason"].lower()


def test_predict_price_respects_bounds():
    """Test that predictions respect min/max price bounds"""
    model = PriceModel()
    
    features = {
        "current_price": 20.0,
        "cost_price": 10.0,
        "inventory": 0,  # Very low inventory
        "stock_age_days": 10,
        "min_price": 18.0,
        "max_price": 22.0,
        "strategy": "revenue_maximize"
    }
    
    result = model.predict_price(features)
    
    assert features["min_price"] <= result["new_price"] <= features["max_price"]
