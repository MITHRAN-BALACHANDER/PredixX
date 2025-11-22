# serve_api_v5.py
import io, requests, numpy as np, pandas as pd, joblib
from fastapi import FastAPI
from pydantic import BaseModel
from PIL import Image, UnidentifiedImageError
from scipy.sparse import hstack, csr_matrix
from features import extract_numeric_specs
from sentence_transformers import SentenceTransformer
import torch
from transformers import CLIPModel, CLIPProcessor

# ---------------- artifacts ----------------
tfidf_text = joblib.load("artifacts/tfidf_text_v5.pkl")
text_feature_cols = joblib.load("artifacts/text_feature_cols_v5.pkl")
text_model = joblib.load("artifacts/model_text_v5.pkl")
image_model = joblib.load("artifacts/model_image_v5.pkl")

# mpnet model for runtime text embedding
mpnet = SentenceTransformer("all-mpnet-base-v2")

# CLIP for image embedding
device = "cuda" if torch.cuda.is_available() else "cpu"
clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32").to(device).eval()
clip_proc  = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

app = FastAPI(title="Price Predictor v5 (MPNet + Quality + Fusion)")

class Item(BaseModel):
    catalog_content: str
    image_link: str | None = None
    sample_id: int | None = None

def image_quality_from_pil(img: Image.Image) -> float:
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

def embed_image_and_quality(url: str):
    if not url:
        return np.zeros((512,), dtype=np.float32), 0.0
    try:
        r = requests.get(url, timeout=8)
        img = Image.open(io.BytesIO(r.content)).convert("RGB")
    except Exception:
        return np.zeros((512,), dtype=np.float32), 0.0

    # CLIP embed
    with torch.no_grad():
        inputs = clip_proc(images=[img], return_tensors="pt", padding=True)
        inputs = {k: v.to(device) for k, v in inputs.items()}
        emb = clip_model.get_image_features(**inputs)[0]
        emb = (emb / emb.norm()).cpu().float().numpy()

    q = image_quality_from_pil(img)
    return emb, float(q)

@app.post("/predict")
def predict(item: Item):
    text = item.catalog_content or ""

    # ---- text pipeline: MPNet + TFIDF + numeric
    mpnet_vec = mpnet.encode([text], convert_to_numpy=True)[0]
    X_tfidf = tfidf_text.transform([text])
    num = pd.DataFrame([extract_numeric_specs(text)]).fillna(0.0)
    num = num.reindex(columns=text_feature_cols, fill_value=0.0)

    from scipy.sparse import csr_matrix
    X_mpnet = csr_matrix(mpnet_vec.reshape(1, -1))
    X_text_all = hstack([X_tfidf, X_mpnet, num.values])
    pred_text = np.expm1(text_model.predict(X_text_all))[0]

    # ---- image pipeline
    img_vec, q = embed_image_and_quality(item.image_link)
    X_img_all = np.hstack([img_vec.reshape(1, -1), np.array([[q]])])
    pred_img = np.expm1(image_model.predict(X_img_all))[0]

    # ---- fuse (0.9 text, 0.1 image)
    final_price = float(max(0.01, 0.9 * pred_text + 0.1 * pred_img))

    return {
        "sample_id": item.sample_id,
        "price": final_price,
        "text_price": float(pred_text),
        "image_price": float(pred_img),
        "image_quality": float(q),
        "fusion": "0.9*text + 0.1*image"
    }
