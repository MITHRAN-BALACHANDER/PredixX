# train_image_model.py

import pandas as pd
import numpy as np
import joblib
from scipy.sparse import csr_matrix
import lightgbm as lgb

print(">> Loading CLIP embeddings...")
embs = np.load("embeddings/clip_b32_train.npy")
ids  = np.load("embeddings/clip_b32_train_ids.npy")

df = pd.read_csv("data/train.csv")
# align embeddings by sample_id
id2row = {int(s):i for i,s in enumerate(ids)}
idx = [id2row[int(x)] for x in df["sample_id"]]
X_img = csr_matrix(embs[idx])

y = np.log1p(df["price"].astype(float).values)

print(">> Training image model...")
train_data = lgb.Dataset(X_img, label=y)

params = {
    "objective": "regression",
    "metric": "rmse",
    "learning_rate": 0.05,
    "num_leaves": 160,
    "feature_fraction": 0.8
}

model = lgb.train(params, train_data, num_boost_round=1200)

joblib.dump(model, "artifacts/model_image.pkl")

print("✅ Saved: model_image.pkl")
