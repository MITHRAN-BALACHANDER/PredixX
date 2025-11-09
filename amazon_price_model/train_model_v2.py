# train_model_v2.py

import pandas as pd
import numpy as np
import joblib

from sklearn.feature_extraction.text import TfidfVectorizer
from scipy.sparse import hstack

import lightgbm as lgb
from features import extract_numeric_specs

# ---------------------------
# load train data
# ---------------------------
df = pd.read_csv("data/train.csv")

X_text = df["catalog_content"].fillna("")
y = np.log1p(df["price"].astype(float).values)   # log target

# ---------------------------
# numeric structured features
# ---------------------------
numeric_dicts = [extract_numeric_specs(x) for x in X_text]
numeric_df = pd.DataFrame(numeric_dicts).fillna(0.0)

# ---------------------------
# TF-IDF
# ---------------------------
tfidf = TfidfVectorizer(
    max_features=250000,
    ngram_range=(1,2),
    min_df=2
)

X_tfidf = tfidf.fit_transform(X_text)

# combine sparse text + dense numeric
X_all = hstack([X_tfidf, numeric_df.values])

# ---------------------------
# LightGBM model
# ---------------------------
train_data = lgb.Dataset(X_all, label=y)

params = {
    "objective": "regression",
    "metric": "rmse",
    "learning_rate": 0.05,
    "num_leaves": 128,
    "feature_fraction": 0.8,
    "bagging_fraction": 0.8,
    "bagging_freq": 1,
}

model = lgb.train(params, train_data, num_boost_round=1200)

# ---------------------------
# save artifacts
# ---------------------------
joblib.dump(tfidf, "artifacts/tfidf_v2.pkl")
joblib.dump(model, "artifacts/lgbm_v2.pkl")
joblib.dump(numeric_df.columns.tolist(), "artifacts/feature_cols_v2.pkl")

print("✅ Training v2 complete!")
print("Saved tfidf_v2.pkl + lgbm_v2.pkl + feature_cols_v2.pkl")
