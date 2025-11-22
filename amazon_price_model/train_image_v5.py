# train_image_v5.py
import os, hashlib, time
import numpy as np
import pandas as pd
import joblib
from pathlib import Path
from PIL import Image, UnidentifiedImageError
from scipy.sparse import csr_matrix
import lightgbm as lgb
from tqdm import tqdm

ART = Path("artifacts"); ART.mkdir(exist_ok=True)
EMB = Path("embeddings")
IMG_DIR = Path("image_cache")
DATA = Path("data")

def safe_filename(url: str) -> str:
    h = hashlib.blake2b(url.encode("utf-8"), digest_size=16).hexdigest()
    return f"{h}.jpg"

def image_quality_score(path: Path):
    try:
        im = Image.open(path).convert("L")
        arr = np.asarray(im).astype(float)
        brightness = arr.mean()
        contrast = arr.std()
        gy, gx = np.gradient(arr)
        sharpness = np.mean(np.abs(gx)) + np.mean(np.abs(gy))
        # normalize by simple scale factors
        return float(0.35 * contrast + 0.35 * sharpness + 0.3 * brightness)
    except Exception:
        return 0.0

print("Loading train.csv and embeddings...")
df = pd.read_csv(DATA / "train.csv")
clip_embs = np.load(EMB / "clip_b32_train.npy")
clip_ids = np.load(EMB / "clip_b32_train_ids.npy")  # alignment order used during embedding save

# map sample_id -> row in clip_embs
id2row = {int(s): i for i, s in enumerate(clip_ids)}

# compute quality scores aligned to train order
quality = []
for sid, url in tqdm(zip(df["sample_id"], df["image_link"]), total=len(df)):
    try:
        fname = safe_filename(str(url))
        p = IMG_DIR / fname
        if p.exists():
            q = image_quality_score(p)
        else:
            q = 0.0
    except Exception:
        q = 0.0
    quality.append(q)

quality = np.array(quality, dtype=np.float32)
np.save(ART / "image_quality_train_v5.npy", quality)

# align embeddings by sample_id
idx = [id2row[int(sid)] for sid in df["sample_id"].tolist()]
X_img = clip_embs[idx]   # shape (N,512)

# append quality feature as last column
X_img_with_q = np.hstack([X_img, quality.reshape(-1,1)])  # shape (N, 513)

# train LightGBM on image-only features (log price)
y = np.log1p(df["price"].astype(float).values)
print("Training image LightGBM...")
dtrain = lgb.Dataset(X_img_with_q, label=y)
params = {
    "objective": "regression",
    "metric": "rmse",
    "learning_rate": 0.05,
    "num_leaves": 140,
    "feature_fraction": 0.8
}
model = lgb.train(params, dtrain, num_boost_round=900)
joblib.dump(model, ART / "model_image_v5.pkl")

print("✅ Saved image model & quality array")
