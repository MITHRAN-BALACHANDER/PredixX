# Model Integration Guide

## Current Model Files Available

The following model artifacts are available in `amazon_price_model/artifacts/`:

- `model_text_v5.pkl` - Text-based pricing model
- `model_image_v5.pkl` - Image-based pricing model  
- `tfidf_text_v5.pkl` - TF-IDF vectorizer for text processing
- `text_feature_cols_v5.pkl` - Feature columns for text model
- `image_quality_train_v5.npy` - Image quality training data

## Integration Status

✓ **Models are now integrated into the DPE backend!**

The backend automatically loads these models from the mounted volume at `/app/models/`.

## How It Works

1. **Volume Mapping**: `docker-compose.yml` maps `./amazon_price_model/artifacts` to `/app/models`
2. **Auto-Loading**: `app/ml/inference.py` automatically loads models on startup
3. **Hybrid Approach**: Uses real models when available, falls back to rule-based pricing

## Verifying Model Loading

### Option 1: Check Docker Logs
```bash
docker-compose logs backend | grep -i "model"
```

You should see:
```
✓ Text model loaded successfully
✓ Image model loaded successfully
✓ TF-IDF vectorizer loaded successfully
✓ Real models are available and will be used for predictions
```

### Option 2: Run Verification Script
```bash
# Inside the backend container
docker-compose exec backend python verify_models.py
```

### Option 3: Test via API
```bash
# Get a price recommendation (requires authentication)
curl -X POST http://localhost:8000/api/v1/price/recommend \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": 1
  }'
```

The response will include `"model_used": "real_model"` or `"model_used": "rule_based"`.

## Model Usage in Predictions

The system now follows this flow:

1. **Load Models**: On startup, loads all `.pkl` and `.npy` files from `/app/models/`
2. **Predict**: When `/api/v1/price/recommend` is called:
   - First tries to use real ML models
   - Falls back to rule-based predictions if models can't make prediction
3. **Response**: Includes `model_used` field to indicate which approach was used

## Full Model Integration (Future)

To use the models for actual predictions (not just loading), you need to:

1. **Understand Model Features**: Determine what features your models expect
2. **Feature Engineering**: Extract/compute those features from product data
3. **Update `predict_with_real_model()`**: Implement proper feature preparation and prediction
4. **Test**: Verify predictions match expected behavior

### Example Integration (Pseudocode)

```python
def predict_with_real_model(self, features: Dict[str, Any]) -> Optional[float]:
    try:
        # Extract product title for text model
        title = features.get("title", "")
        
        # Vectorize text
        if self.tfidf and self.model_text and title:
            text_features = self.tfidf.transform([title])
            text_prediction = self.model_text.predict(text_features)[0]
            return float(text_prediction)
        
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None
```

## Testing Locally (Without Docker)

```bash
cd dpe-backend

# Set environment variable to point to models
export MODEL_PATH="../amazon_price_model/artifacts"  # Linux/Mac
# OR
set MODEL_PATH="..\amazon_price_model\artifacts"  # Windows

# Run verification
python verify_models.py
```

## Troubleshooting

### Models Not Loading

**Check volume mount:**
```bash
docker-compose exec backend ls -la /app/models/
```

Should show all `.pkl` and `.npy` files.

**Check permissions:**
```bash
docker-compose exec backend ls -l /app/models/model_text_v5.pkl
```

**View detailed logs:**
```bash
docker-compose logs backend | tail -50
```

### Import Errors

If you see "cannot import joblib", rebuild the backend:
```bash
docker-compose build backend
docker-compose up -d backend
```

## Model API Response

When models are loaded, API responses include:

```json
{
  "new_price": 22.50,
  "confidence": 0.92,
  "reason": "ML Model prediction",
  "predicted_revenue_change": 5.2,
  "stockout_prediction": 0.15,
  "model_used": "real_model"
}
```

vs rule-based:

```json
{
  "new_price": 21.00,
  "confidence": 0.85,
  "reason": "Revenue maximization: Low inventory",
  "predicted_revenue_change": 8.0,
  "stockout_prediction": 0.20,
  "model_used": "rule_based"
}
```

## Next Steps

1. ✓ Models are loaded
2. ⏭ Implement feature engineering for your specific model
3. ⏭ Update `predict_with_real_model()` with actual prediction logic
4. ⏭ Test predictions against known good results
5. ⏭ Monitor model performance in production

---

**The infrastructure is ready - models are loaded and accessible!** 🚀
