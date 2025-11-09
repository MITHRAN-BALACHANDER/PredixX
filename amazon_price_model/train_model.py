# train_model.py

import pandas as pd
import numpy as np
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import Ridge

# -------------------------
# 1) LOAD TRAIN DATA
# -------------------------
df = pd.read_csv("data/train.csv")

X = df["catalog_content"].fillna("")
y = np.log1p(df["price"].astype(float).values)   # log target

# -------------------------
# 2) TF-IDF + RIDGE TRAIN
# -------------------------
tfidf = TfidfVectorizer(
    max_features=200000,
    ngram_range=(1,2),
    min_df=2
)

X_tfidf = tfidf.fit_transform(X)

model = Ridge(alpha=2.0, random_state=42)
model.fit(X_tfidf, y)

# -------------------------
# 3) SAVE ARTIFACTS
# -------------------------
joblib.dump(tfidf, "artifacts/tfidf.pkl")
joblib.dump(model, "artifacts/ridge.pkl")

print("✅ Training complete.")
print("Artifacts saved to: artifacts/tfidf.pkl & artifacts/ridge.pkl")
