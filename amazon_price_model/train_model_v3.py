# train_model_v3.py

import pandas as pd
import numpy as np
import joblib
import lightgbm as lgb
from scipy.sparse import hstack

from sklearn.feature_extraction.text import TfidfVectorizer
from features import extract_numeric_specs

# ---- 1) load train ----
df = pd.read_csv("data/train.csv")

X_text = df["catalog_content"].fillna("")
y = np.log1p(df["price"].astype(float).values)

# ---- 2) numeric features ----
numeric_dicts = [extract_numeric_specs(x) for x in X_text]
numeric_df = pd.DataFrame(numeric_dicts).fillna(0.0)

# save column order for later
feature_cols = numeric_df.columns.tolist()
joblib.dump(feature_cols, "artifacts/feature_cols_v3.pkl")

# ---- 3) text TFIDF ----
tfidf = TfidfVectorizer(
    max_features=250000,
    ngram_range=(1,2),
    min_df=2
)
X_tfidf = tfidf.fit_transform(X_text)
joblib.dump(tfidf, "artifacts/tfidf_v3.pkl")

# ---- 4) image embeddings ----
img_embs = np.load("embeddings/clip_b32_train.npy")  # shape (75000, 512)
# convert numpy to sparse-like shape
from scipy.sparse import csr_matrix
X_img = csr_matrix(img_embs)

# ---- 5) combine all ----
X_all = hstack([X_tfidf, numeric_df.values, X_img])

# ---- 6) train LGBM ----
train_data = lgb.Dataset(X_all, label=y)

params = {
    "objective": "regression",
    "metric": "rmse",
    "learning_rate": 0.05,
    "num_leaves": 200,
    "feature_fraction": 0.8,
    "bagging_fraction": 0.8,
    "bagging_freq": 1,
}

model = lgb.train(params, train_data, num_boost_round=1500)

joblib.dump(model, "artifacts/lgbm_v3.pkl")

print("✅ v3 training complete")
print("saved: tfidf_v3.pkl / feature_cols_v3.pkl / lgbm_v3.pkl")
