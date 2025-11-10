# quick_val_v3.py
import pandas as pd, numpy as np, joblib
from sklearn.model_selection import train_test_split
from scipy.sparse import hstack, csr_matrix
import lightgbm as lgb
from features import extract_numeric_specs

def smape(y_true, y_pred):
    denom = (np.abs(y_true) + np.abs(y_pred)) / 2
    denom = np.where(denom==0,1e-6,denom)
    return np.mean(np.abs(y_true - y_pred) / denom) * 100

print(">> load train")
train = pd.read_csv("data/train.csv")

print(">> load CLIP aligned embeddings")
clip = np.load("embeddings/clip_b32_train.npy")
clip_ids = np.load("embeddings/clip_b32_train_ids.npy")
id2row = {int(s):i for i,s in enumerate(clip_ids)}
idx = [id2row[int(x)] for x in train["sample_id"]]
X_img = csr_matrix(clip[idx])

# text numeric
from sklearn.feature_extraction.text import TfidfVectorizer
tfidf = joblib.load("artifacts/tfidf_v3.pkl")
X_text = tfidf.transform(train["catalog_content"].fillna(""))

num = pd.DataFrame([extract_numeric_specs(t) for t in train["catalog_content"]]).fillna(0.0)
feat_cols = joblib.load("artifacts/feature_cols_v3.pkl")
num = num.reindex(columns=feat_cols, fill_value=0.0)

X_all = hstack([X_text, num.values, X_img])
y = train["price"].values

# simple split
X_tr, X_va, y_tr, y_va = train_test_split(X_all, y, test_size=0.1, random_state=42)

model = joblib.load("artifacts/lgbm_v3.pkl")
pred = np.expm1(model.predict(X_va))
pred = np.clip(pred, 0.01, None)

print("quick holdout smape =", smape(y_va, pred), "%")
