import io, requests, numpy as np, pandas as pd, joblib
from fastapi import FastAPI
from pydantic import BaseModel
from PIL import Image
from scipy.sparse import hstack, csr_matrix
from features import extract_numeric_specs

import torch
from transformers import CLIPModel, CLIPProcessor

# === load artifacts ===
tfidf = joblib.load("artifacts/tfidf_v3.pkl")
model = joblib.load("artifacts/lgbm_v3.pkl")
feature_cols = joblib.load("artifacts/feature_cols_v3.pkl")


device = "cuda" if torch.cuda.is_available() else "cpu"
clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32").to(device).eval()
clip_proc  = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

app = FastAPI(title="Price Predictor v3.0")

class Item(BaseModel):
    catalog_content: str
    image_link: str | None = None
    sample_id: int | None = None

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
        inp = {k: v.to(device) for k,v in inp.items()}
        em = clip_model.get_image_features(**inp)[0]
        em = em / em.norm()
        return em.cpu().float().numpy()

@app.post("/predict")
def predict(item: Item):
    text = item.catalog_content or ""

    X_text = tfidf.transform([text])

    num = pd.DataFrame([extract_numeric_specs(text)]).fillna(0.0)
    num = num.reindex(columns=feature_cols, fill_value=0.0)

    img_vec = embed_image(item.image_link)
    X_img = csr_matrix(img_vec.reshape(1, -1))

    X_all = hstack([X_text, num.values, X_img])
    price = float(max(np.expm1(model.predict(X_all))[0], 0.01))
    return {"sample_id": item.sample_id, "price": price}
