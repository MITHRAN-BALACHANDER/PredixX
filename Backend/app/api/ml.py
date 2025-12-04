"""
ML Price Prediction API Endpoint
Accepts product name, description, quantity, and optional image for price prediction
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from typing import Optional

from app.core.security import get_current_user
from app.models.user import User

router = APIRouter(prefix="/ml", tags=["ml"])


@router.post("/predict")
async def predict_price(
    product_name: str = Form(..., description="Name of the product"),
    description: str = Form("", description="Product description"),
    quantity: int = Form(1, description="Product quantity"),
    image: Optional[UploadFile] = File(None, description="Product image"),
    current_user: User = Depends(get_current_user)
):
    """
    Predict optimal price for a product using ML models.
    
    Uses a fusion of text (MPNet + TF-IDF) and image (CLIP) models
    to predict the optimal price.
    
    - **product_name**: Name/title of the product (required)
    - **description**: Detailed product description
    - **quantity**: Number of items (for pack pricing)
    - **image**: Product image file (JPEG/PNG)
    """
    try:
        from app.ml.price_predictor import get_predictor
        
        predictor = get_predictor()
        
        # Read image bytes if provided
        image_bytes = None
        if image:
            image_bytes = await image.read()
        
        # Get prediction
        result = predictor.predict(
            product_name=product_name,
            description=description,
            quantity=quantity,
            image_bytes=image_bytes
        )
        
        return {
            "success": True,
            "prediction": result
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {str(e)}"
        )


@router.post("/predict-json")
async def predict_price_json(
    data: dict,
    current_user: User = Depends(get_current_user)
):
    """
    Predict price using JSON payload (no image).
    
    Request body:
    ```json
    {
        "product_name": "Product Title",
        "description": "Product description...",
        "quantity": 1
    }
    ```
    """
    try:
        from app.ml.price_predictor import get_predictor
        
        predictor = get_predictor()
        
        result = predictor.predict(
            product_name=data.get("product_name", ""),
            description=data.get("description", ""),
            quantity=data.get("quantity", 1),
            image_bytes=None
        )
        
        return {
            "success": True,
            "prediction": result
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {str(e)}"
        )


@router.get("/status")
async def get_ml_status(
    current_user: User = Depends(get_current_user)
):
    """Check ML model loading status"""
    try:
        from app.ml.price_predictor import get_predictor
        import os
        
        predictor = get_predictor()
        
        # Check which models are loaded
        models_status = {
            "tfidf_loaded": predictor.tfidf is not None,
            "text_model_loaded": predictor.text_model is not None,
            "image_model_loaded": predictor.image_model is not None,
            "mpnet_loaded": predictor.mpnet is not None,
            "clip_loaded": predictor.clip_model is not None,
            "device": predictor.device
        }
        
        # Check artifacts directory
        from app.ml.price_predictor import ARTIFACTS_DIR
        artifacts_exist = os.path.exists(ARTIFACTS_DIR)
        
        return {
            "success": True,
            "models_loaded": predictor._loaded,
            "artifacts_directory": ARTIFACTS_DIR,
            "artifacts_exist": artifacts_exist,
            "status": models_status
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
