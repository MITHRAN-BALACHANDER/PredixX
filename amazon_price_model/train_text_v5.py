# train_text_v5.py
import os
import numpy as np
import pandas as pd
import joblib
from pathlib import Path
from scipy.sparse import hstack, csr_matrix
from sklearn.feature_extraction.text import TfidfVectorizer
import lightgbm as lgb
from sentence_transformers import SentenceTransformer
from features import extract_numeric_specs

ART = Path("artifacts"); ART.mkdir(exist_ok=True)
DATA = Path("data")

print("Loading train.csv...")
df = pd.read_csv(DATA / "train.csv")
texts = df["catalog_content"].fillna("").astype(str).tolist()
y = np.log1p(df["price"].astype(float).values)

# ---------------- MPNet embeddings (dense)
print("Computing MPNet embeddings (this may take a few minutes)...")
mpnet = SentenceTransformer("all-mpnet-base-v2")
mpnet_embs = mpnet.encode(texts, show_progress_bar=True, batch_size=64, convert_to_numpy=True)
# save dense embeddings so we don't need to recompute
np.save(ART / "mpnet_train_v5.npy", mpnet_embs)

# ---------------- TF-IDF (sparse)
print("Fitting TF-IDF...")
tfidf = TfidfVectorizer(max_features=100000, ngram_range=(1,2), min_df=2)
X_tfidf = tfidf.fit_transform(texts)
joblib.dump(tfidf, ART / "tfidf_text_v5.pkl")

# ---------------- numeric features
print("Extracting numeric features from text...")
numeric_list = [extract_numeric_specs(t) for t in texts]
numeric_df = pd.DataFrame(numeric_list).fillna(0.0)
feature_cols = numeric_df.columns.tolist()
joblib.dump(feature_cols, ART / "text_feature_cols_v5.pkl")

# ---------------- combine: TF-IDF (sparse) + MPNet (dense) + numeric (dense)
print("Combining features...")
from scipy.sparse import csr_matrix, hstack
X_mpnet = csr_matrix(mpnet_embs)             # treat dense as sparse-friendly block
X_all = hstack([X_tfidf, X_mpnet, numeric_df.values])

# ---------------- train LightGBM on Y = log(price)
print("Training text LightGBM...")
dtrain = lgb.Dataset(X_all, label=y)
params = {
    "objective": "regression",
    "metric": "rmse",
    "learning_rate": 0.05,
    "num_leaves": 180,
    "feature_fraction": 0.8,
    "bagging_fraction": 0.8,
    "bagging_freq": 1,
}
model = lgb.train(params, dtrain, num_boost_round=1200)
joblib.dump(model, ART / "model_text_v5.pkl")

print("✅ Saved text artifacts: tfidf_text_v5.pkl, text_feature_cols_v5.pkl, model_text_v5.pkl, mpnet_train_v5.npy")
