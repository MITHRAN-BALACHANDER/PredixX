# predict_v2.py

import pandas as pd
import numpy as np
import joblib
from scipy.sparse import hstack
from features import extract_numeric_specs

# -------------------------
# LOAD TEST
# -------------------------
df_test = pd.read_csv("data/test.csv")

X_text = df_test["catalog_content"].fillna("")

# -------------------------
# LOAD ARTIFACTS
# -------------------------
tfidf = joblib.load("artifacts/tfidf_v2.pkl")
model = joblib.load("artifacts/lgbm_v2.pkl")
feature_cols = joblib.load("artifacts/feature_cols_v2.pkl")

# -------------------------
# TEXT FEATURES
# -------------------------
X_tfidf = tfidf.transform(X_text)

# -------------------------
# NUMERIC FEATURES
# -------------------------
numeric_dicts = [extract_numeric_specs(x) for x in X_text]
numeric_df = pd.DataFrame(numeric_dicts).fillna(0.0)

# ensure same column order
numeric_df = numeric_df[feature_cols]

# -------------------------
# COMBINE
# -------------------------
X_all = hstack([X_tfidf, numeric_df.values])

# -------------------------
# PREDICT
# -------------------------
pred_log = model.predict(X_all)
pred_price = np.expm1(pred_log)
pred_price = np.clip(pred_price, 0.01, None)

# -------------------------
# SAVE CSV
# -------------------------
submission = pd.DataFrame({
    "sample_id": df_test["sample_id"],
    "price": pred_price
})

submission.to_csv("submission_v2.csv", index=False)

print("✅ v2 predictions done: submission_v2.csv")
