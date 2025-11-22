import io, requests, numpy as np, pandas as pd, joblib
from fastapi import FastAPI
from pydantic import BaseModel
from PIL import Image
from scipy.sparse import hstack, csr_matrix
from features import extract_numeric_specs

import torch
from transformers import CLIPModel, CLIPProcessor

# ================================
# Load TEXT MODEL artifacts
# ================================
tfidf_text = joblib.load("artifacts/tfidf_text.pkl")
text_feature_cols = joblib.load("artifacts/text_feature_cols.pkl")
text_model = joblib.load("artifacts/model_text.pkl")

# ================================
# Load IMAGE MODEL
# ================================
image_model = joblib.load("artifacts/model_image.pkl")

# load CLIP once
device = "cuda" if torch.cuda.is_available() else "cpu"
clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32").to(device).eval()
clip_proc  = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

# ================================
# FastAPI app init
# ================================
app = FastAPI(title="Price Predictor v4.0 (Fusion Model)")

# Request format
class Item(BaseModel):
    catalog_content: str
    image_link: str | None = None
    sample_id: int | None = None

# ================================
# CLIP image embedder (for inference)
# ================================
def embed_image(url: str) -> np.ndarray:
    if not url:
        return np.zeros((512,), dtype=np.float32)

    try:
        r = requests.get(url, timeout=8)
        img = Image.open(io.BytesIO(r.content)).convert("RGB")
    except:
        return np.zeros((512,), dtype=np.float32)

    with torch.no_grad():
        inp = clip_proc(images=[img], return_tensors="pt", padding=True)
        inp = {k: v.to(device) for k, v in inp.items()}
        emb = clip_model.get_image_features(**inp)[0]
        emb = emb / emb.norm()  # normalize
        return emb.cpu().float().numpy()

# ================================
# API Endpoint: /predict
# ================================
@app.post("/predict")
def predict(item: Item):

    # ========== TEXT PIPELINE ==========
    text = item.catalog_content or ""

    X_tfidf = tfidf_text.transform([text])

    num = pd.DataFrame([extract_numeric_specs(text)]).fillna(0.0)
    num = num.reindex(columns=text_feature_cols, fill_value=0.0)

    X_text_total = hstack([X_tfidf, num.values])
    pred_text = np.expm1(text_model.predict(X_text_total))[0]


    # ========== IMAGE PIPELINE ==========
    img_vec = embed_image(item.image_link)
    X_img = csr_matrix(img_vec.reshape(1, -1))

    pred_image = np.expm1(image_model.predict(X_img))[0]


    # ========== FUSION ==========
    FINAL_PRED = 0.7 * pred_text + 0.3 * pred_image
    FINAL_PRED = float(max(FINAL_PRED, 0.01))


    return {
        "sample_id": item.sample_id,
        "price": FINAL_PRED,
        "text_price": float(pred_text),
        "image_price": float(pred_image),
        "fusion": "0.7*text + 0.3*image"
    }
