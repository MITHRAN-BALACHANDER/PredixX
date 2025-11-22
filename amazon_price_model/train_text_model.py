# train_text_model.py

import pandas as pd
import numpy as np
import joblib
from scipy.sparse import hstack
from sklearn.feature_extraction.text import TfidfVectorizer
import lightgbm as lgb
from features import extract_numeric_specs

print(">> Loading train.csv...")
df = pd.read_csv("data/train.csv")

X_text = df["catalog_content"].fillna("")
y = np.log1p(df["price"].astype(float).values)

# numeric features
num = pd.DataFrame([extract_numeric_specs(t) for t in X_text]).fillna(0.0)
feature_cols = num.columns.tolist()

# TF-IDF
print(">> Building TF-IDF...")
tfidf = TfidfVectorizer(max_features=250000, ngram_range=(1,2), min_df=2)
X_tfidf = tfidf.fit_transform(X_text)

# fuse text + numeric only
X_all = hstack([X_tfidf, num.values])

# train LightGBM
print(">> Training text model...")
train_data = lgb.Dataset(X_all, label=y)
params = {
    "objective": "regression",
    "metric": "rmse",
    "learning_rate": 0.05,
    "num_leaves": 180,
    "feature_fraction": 0.8,
    "bagging_fraction": 0.8,
    "bagging_freq": 1
}

model = lgb.train(params, train_data, num_boost_round=1500)

# save artifacts
joblib.dump(tfidf, "artifacts/tfidf_text.pkl")
joblib.dump(feature_cols, "artifacts/text_feature_cols.pkl")
joblib.dump(model, "artifacts/model_text.pkl")

print("✅ Saved: tfidf_text.pkl, text_feature_cols.pkl, model_text.pkl")
