# predict_v3.py

import pandas as pd
import numpy as np
import joblib
from scipy.sparse import hstack, csr_matrix
from features import extract_numeric_specs

# ---- load test ----
df_test = pd.read_csv("data/test.csv")
X_text = df_test["catalog_content"].fillna("")

# ---- load artifacts ----
tfidf = joblib.load("artifacts/tfidf_v3.pkl")
model = joblib.load("artifacts/lgbm_v3.pkl")
feature_cols = joblib.load("artifacts/feature_cols_v3.pkl")

# ---- numeric features ----
numeric_dicts = [extract_numeric_specs(x) for x in X_text]
numeric_df = pd.DataFrame(numeric_dicts).fillna(0.0)
numeric_df = numeric_df[feature_cols]

# ---- text tfidf ----
X_tfidf = tfidf.transform(X_text)

# ---- image embeddings ----
img_embs = np.load("embeddings/clip_b32_test.npy")
X_img = csr_matrix(img_embs)

# ---- fuse all ----
X_all = hstack([X_tfidf, numeric_df.values, X_img])

# ---- predict ----
pred_log = model.predict(X_all)
pred_price = np.expm1(pred_log)
pred_price = np.clip(pred_price, 0.01, None)

# ---- save submission ----
submission = pd.DataFrame({
    "sample_id": df_test["sample_id"],
    "price": pred_price
})
submission.to_csv("submission_v3.csv", index=False)

print("✅ v3 submission generated -> submission_v3.csv")
