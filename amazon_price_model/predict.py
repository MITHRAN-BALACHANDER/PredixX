# predict.py

import pandas as pd
import numpy as np
import joblib

# -------------------------
# 1) LOAD TEST DATA
# -------------------------
df_test = pd.read_csv("data/test.csv")

X_test = df_test["catalog_content"].fillna("")

# -------------------------
# 2) LOAD ARTIFACTS
# -------------------------
tfidf = joblib.load("artifacts/tfidf.pkl")
model = joblib.load("artifacts/ridge.pkl")

# -------------------------
# 3) TRANSFORM TEST TEXT
# -------------------------
X_tfidf_test = tfidf.transform(X_test)

# -------------------------
# 4) PREDICT
# -------------------------
pred_log = model.predict(X_tfidf_test)
pred_price = np.expm1(pred_log)     # reverse log1p

# clip small negatives (shouldn’t happen but safe)
pred_price = np.clip(pred_price, 0.01, None)

# -------------------------
# 5) SAVE SUBMISSION FILE
# -------------------------
submission = pd.DataFrame({
    "sample_id": df_test["sample_id"],
    "price": pred_price
})

submission.to_csv("submission.csv", index=False)

print("✅ prediction complete")
print("submission.csv generated")
