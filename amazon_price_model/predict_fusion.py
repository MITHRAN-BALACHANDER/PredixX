# predict_fusion.py

import pandas as pd
import numpy as np
import joblib
from scipy.sparse import hstack, csr_matrix
from features import extract_numeric_specs

# load test
df = pd.read_csv("data/test.csv")
X_text = df["catalog_content"].fillna("")

# load text artifacts
tfidf = joblib.load("artifacts/tfidf_text.pkl")
text_cols = joblib.load("artifacts/text_feature_cols.pkl")
text_model = joblib.load("artifacts/model_text.pkl")

# numeric
num = pd.DataFrame([extract_numeric_specs(t) for t in X_text]).fillna(0.0)
num = num.reindex(columns=text_cols, fill_value=0.0)

# text prediction
X_tfidf = tfidf.transform(X_text)
X_text_all = hstack([X_tfidf, num.values])
pred_text = np.expm1(text_model.predict(X_text_all))

# image prediction
clip_embs = np.load("embeddings/clip_b32_test.npy")
clip_ids  = np.load("embeddings/clip_b32_test_ids.npy")

id2row = {int(s): i for i, s in enumerate(clip_ids)}
idx = [id2row[int(x)] for x in df["sample_id"]]
X_img = csr_matrix(clip_embs[idx])

img_model = joblib.load("artifacts/model_image.pkl")
pred_img = np.expm1(img_model.predict(X_img))

# fusion
final_pred = 0.7 * pred_text + 0.3 * pred_img
final_pred = np.clip(final_pred, 0.01, None)

sub = pd.DataFrame({
    "sample_id": df["sample_id"],
    "price": final_pred
})

sub.to_csv("submission_fusion.csv", index=False)
print("✅ Saved: submission_fusion.csv")
