# predict_fusion_v5.py
import numpy as np
import pandas as pd
import joblib
from pathlib import Path
from scipy.sparse import hstack, csr_matrix
from sentence_transformers import SentenceTransformer
from features import extract_numeric_specs

ART = Path("artifacts")
EMB = Path("embeddings")
DATA = Path("data")

print("Loading test.csv...")
df_test = pd.read_csv(DATA / "test.csv")
texts = df_test["catalog_content"].fillna("").astype(str).tolist()

# ---- load text model artifacts ----
tfidf = joblib.load(ART / "tfidf_text_v5.pkl")
text_feature_cols = joblib.load(ART / "text_feature_cols_v5.pkl")
text_model = joblib.load(ART / "model_text_v5.pkl")
mpnet_embs_train_path = ART / "mpnet_train_v5.npy"

# compute MPNet for test (or you may precompute and save to disk)
print("Computing MPNet test embeddings...")
mpnet = SentenceTransformer("all-mpnet-base-v2")
mpnet_test = mpnet.encode(texts, show_progress_bar=True, batch_size=64, convert_to_numpy=True)

# text features
X_tfidf = tfidf.transform(texts)
from scipy.sparse import csr_matrix
X_mpnet = csr_matrix(mpnet_test)
# numeric
numeric_list = [extract_numeric_specs(t) for t in texts]
numeric_df = pd.DataFrame(numeric_list).fillna(0.0)
numeric_df = numeric_df.reindex(columns=text_feature_cols, fill_value=0.0)

X_text_all = hstack([X_tfidf, X_mpnet, numeric_df.values])
pred_text_log = text_model.predict(X_text_all)
pred_text = np.expm1(pred_text_log)

# ---- image predictions ----
clip_embs = np.load(EMB / "clip_b32_test.npy")
clip_ids = np.load(EMB / "clip_b32_test_ids.npy")
id2row = {int(s): i for i, s in enumerate(clip_ids)}
idx = [id2row[int(sid)] for sid in df_test["sample_id"].tolist()]
X_img = clip_embs[idx]

# load image quality computed previously if available, else zeros
qpath = ART / "image_quality_train_v5.npy"  # not for test, but try embeddings dir
try:
    # If you saved test quality similarly, load it. Otherwise fallback zeros.
    q_test = np.load(ART / "image_quality_test_v5.npy")
    if len(q_test) != len(df_test):
        q_test = np.zeros(len(df_test), dtype=np.float32)
except Exception:
    q_test = np.zeros(len(df_test), dtype=np.float32)

X_img_with_q = np.hstack([X_img, q_test.reshape(-1, 1)])
image_model = joblib.load(ART / "model_image_v5.pkl")
pred_img = np.expm1(image_model.predict(X_img_with_q))

# ---- fuse with weights text=0.9, image=0.1
final_pred = 0.9 * pred_text + 0.1 * pred_img
final_pred = np.clip(final_pred, 0.01, None)

sub = pd.DataFrame({"sample_id": df_test["sample_id"], "price": final_pred})
sub.to_csv("submission_v5.csv", index=False)
print("✅ Saved submission_v5.csv")
