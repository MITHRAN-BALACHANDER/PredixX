"""
Price Prediction Service using trained ML models from amazon_price_model
Supports text + image fusion for price prediction
"""
import io
import os
import numpy as np
import joblib
from typing import Optional, Tuple
from PIL import Image

# Model artifacts path
ARTIFACTS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "..", "amazon_price_model", "artifacts")


class PricePredictor:
    """Price prediction using text and image fusion models"""
    
    def __init__(self):
        self.tfidf = None
        self.text_feature_cols = None
        self.text_model = None
        self.image_model = None
        self.mpnet = None
        self.clip_model = None
        self.clip_processor = None
        self.device = "cpu"
        self._loaded = False
        
    def load_models(self):
        """Load all model artifacts"""
        if self._loaded:
            return
            
        try:
            # Load text model artifacts
            tfidf_path = os.path.join(ARTIFACTS_DIR, "tfidf_text_v5.pkl")
            text_cols_path = os.path.join(ARTIFACTS_DIR, "text_feature_cols_v5.pkl")
            text_model_path = os.path.join(ARTIFACTS_DIR, "model_text_v5.pkl")
            image_model_path = os.path.join(ARTIFACTS_DIR, "model_image_v5.pkl")
            
            if os.path.exists(tfidf_path):
                self.tfidf = joblib.load(tfidf_path)
                print("✓ TF-IDF vectorizer loaded")
                
            if os.path.exists(text_cols_path):
                self.text_feature_cols = joblib.load(text_cols_path)
                print("✓ Text feature columns loaded")
                
            if os.path.exists(text_model_path):
                self.text_model = joblib.load(text_model_path)
                print("✓ Text model loaded")
                
            if os.path.exists(image_model_path):
                self.image_model = joblib.load(image_model_path)
                print("✓ Image model loaded")
            
            # Load sentence transformer for text embeddings
            try:
                from sentence_transformers import SentenceTransformer
                self.mpnet = SentenceTransformer("all-mpnet-base-v2")
                print("✓ MPNet sentence transformer loaded")
            except Exception as e:
                print(f"⚠ Could not load MPNet: {e}")
            
            # Load CLIP for image embeddings
            try:
                import torch
                from transformers import CLIPModel, CLIPProcessor
                self.device = "cuda" if torch.cuda.is_available() else "cpu"
                self.clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32").to(self.device).eval()
                self.clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
                print(f"✓ CLIP model loaded on {self.device}")
            except Exception as e:
                print(f"⚠ Could not load CLIP: {e}")
            
            self._loaded = True
            print("✓ All models loaded successfully")
            
        except Exception as e:
            print(f"⚠ Error loading models: {e}")
            raise
    
    def extract_numeric_specs(self, text: str) -> dict:
        """Extract numeric specifications from text"""
        import re
        specs = {}
        
        # Weight patterns
        weight_match = re.search(r'(\d+(?:\.\d+)?)\s*(kg|g|lb|oz|pound|gram)', text.lower())
        if weight_match:
            value, unit = float(weight_match.group(1)), weight_match.group(2)
            if unit in ['kg', 'kilogram']:
                specs['weight_kg'] = value
            elif unit in ['g', 'gram']:
                specs['weight_kg'] = value / 1000
            elif unit in ['lb', 'pound']:
                specs['weight_kg'] = value * 0.453592
            elif unit == 'oz':
                specs['weight_kg'] = value * 0.0283495
        
        # Dimension patterns
        dim_match = re.search(r'(\d+(?:\.\d+)?)\s*[xX×]\s*(\d+(?:\.\d+)?)\s*[xX×]?\s*(\d+(?:\.\d+)?)?', text)
        if dim_match:
            specs['dim_1'] = float(dim_match.group(1))
            specs['dim_2'] = float(dim_match.group(2))
            if dim_match.group(3):
                specs['dim_3'] = float(dim_match.group(3))
        
        # Capacity patterns
        cap_match = re.search(r'(\d+(?:\.\d+)?)\s*(ml|l|liter|litre|gallon|oz)', text.lower())
        if cap_match:
            value, unit = float(cap_match.group(1)), cap_match.group(2)
            if unit in ['l', 'liter', 'litre']:
                specs['capacity_ml'] = value * 1000
            elif unit == 'ml':
                specs['capacity_ml'] = value
            elif unit == 'gallon':
                specs['capacity_ml'] = value * 3785.41
        
        # Count/quantity patterns
        count_match = re.search(r'(\d+)\s*(pack|count|piece|pc|pcs|set)', text.lower())
        if count_match:
            specs['count'] = int(count_match.group(1))
        
        return specs
    
    def compute_image_quality(self, img: Image.Image) -> float:
        """Compute image quality score"""
        try:
            im = img.convert("L")
            arr = np.asarray(im).astype(float)
            brightness = arr.mean()
            contrast = arr.std()
            gy, gx = np.gradient(arr)
            sharpness = (np.abs(gx).mean() + np.abs(gy).mean())
            return float(0.35 * contrast + 0.35 * sharpness + 0.3 * brightness)
        except Exception:
            return 0.0
    
    def get_text_embedding(self, text: str) -> np.ndarray:
        """Get MPNet embedding for text"""
        if self.mpnet is None:
            return np.zeros((768,), dtype=np.float32)
        return self.mpnet.encode([text], convert_to_numpy=True)[0]
    
    def get_image_embedding(self, img: Image.Image) -> Tuple[np.ndarray, float]:
        """Get CLIP embedding and quality score for image"""
        if self.clip_model is None or self.clip_processor is None:
            return np.zeros((512,), dtype=np.float32), 0.0
        
        try:
            import torch
            with torch.no_grad():
                inputs = self.clip_processor(images=[img], return_tensors="pt", padding=True)
                inputs = {k: v.to(self.device) for k, v in inputs.items()}
                emb = self.clip_model.get_image_features(**inputs)[0]
                emb = (emb / emb.norm()).cpu().float().numpy()
            
            quality = self.compute_image_quality(img)
            return emb, quality
        except Exception as e:
            print(f"⚠ Error getting image embedding: {e}")
            return np.zeros((512,), dtype=np.float32), 0.0
    
    def predict(
        self,
        product_name: str,
        description: str = "",
        quantity: int = 1,
        image_bytes: Optional[bytes] = None
    ) -> dict:
        """
        Predict price for a product using text and image fusion
        
        Args:
            product_name: Name of the product
            description: Product description
            quantity: Product quantity
            image_bytes: Raw image bytes (optional)
            
        Returns:
            Dictionary with prediction results
        """
        self.load_models()
        
        # Combine text content
        catalog_content = f"{product_name} {description}".strip()
        if quantity > 1:
            catalog_content += f" {quantity} pack"
        
        pred_text = 0.0
        pred_image = 0.0
        image_quality = 0.0
        
        # Text prediction
        if self.text_model is not None and self.tfidf is not None:
            try:
                from scipy.sparse import hstack, csr_matrix
                
                # TF-IDF features
                X_tfidf = self.tfidf.transform([catalog_content])
                
                # MPNet embedding
                mpnet_vec = self.get_text_embedding(catalog_content)
                X_mpnet = csr_matrix(mpnet_vec.reshape(1, -1))
                
                # Numeric features
                import pandas as pd
                numeric_specs = self.extract_numeric_specs(catalog_content)
                num_df = pd.DataFrame([numeric_specs]).fillna(0.0)
                if self.text_feature_cols is not None:
                    num_df = num_df.reindex(columns=self.text_feature_cols, fill_value=0.0)
                
                # Combine all text features
                X_text_all = hstack([X_tfidf, X_mpnet, num_df.values])
                
                # Predict (model outputs log price)
                pred_text_log = self.text_model.predict(X_text_all)[0]
                pred_text = float(np.expm1(pred_text_log))
                
            except Exception as e:
                print(f"⚠ Text prediction error: {e}")
                pred_text = 0.0
        
        # Image prediction
        if image_bytes is not None and self.image_model is not None:
            try:
                img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
                img_emb, image_quality = self.get_image_embedding(img)
                
                # Combine image embedding with quality score
                X_img = np.hstack([img_emb.reshape(1, -1), np.array([[image_quality]])])
                
                # Predict
                pred_img_log = self.image_model.predict(X_img)[0]
                pred_image = float(np.expm1(pred_img_log))
                
            except Exception as e:
                print(f"⚠ Image prediction error: {e}")
                pred_image = 0.0
        
        # Fusion: 0.9 * text + 0.1 * image (matching serve_api_v5.py)
        if pred_text > 0 and pred_image > 0:
            final_price = 0.9 * pred_text + 0.1 * pred_image
            fusion_method = "0.9*text + 0.1*image"
        elif pred_text > 0:
            final_price = pred_text
            fusion_method = "text_only"
        elif pred_image > 0:
            final_price = pred_image
            fusion_method = "image_only"
        else:
            # Fallback estimate based on description length
            final_price = max(9.99, len(catalog_content) * 0.1)
            fusion_method = "fallback"
        
        # Ensure reasonable price
        final_price = max(0.01, final_price)
        
        return {
            "predicted_price": round(final_price, 2),
            "text_price": round(pred_text, 2) if pred_text > 0 else None,
            "image_price": round(pred_image, 2) if pred_image > 0 else None,
            "image_quality": round(image_quality, 2) if image_quality > 0 else None,
            "fusion_method": fusion_method,
            "confidence": 0.85 if fusion_method != "fallback" else 0.3,
            "product_name": product_name,
            "description": description[:200] if description else None,
            "quantity": quantity
        }


# Global predictor instance
_predictor: Optional[PricePredictor] = None


def get_predictor() -> PricePredictor:
    """Get or create the global predictor instance"""
    global _predictor
    if _predictor is None:
        _predictor = PricePredictor()
    return _predictor
