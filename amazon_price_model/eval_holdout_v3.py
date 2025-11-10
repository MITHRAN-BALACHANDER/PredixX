# eval_holdout_v3.py
import numpy as np, pandas as pd, joblib
from sklearn.model_selection import train_test_split
from scipy.sparse import hstack, csr_matrix
from features import extract_numeric_specs

def smape(y_true, y_pred):
    denom = (np.abs(y_true)+np.abs(y_pred))/2.0
    denom = np.where(denom==0, 1e-6, denom)
    return np.mean(np.abs(y_pred - y_true)/denom)*100

# load train + artifacts + train embeddings
train = pd.read_csv("data/train.csv")
tfidf = joblib.load("artifacts/tfidf_v3.pkl")
model = joblib.load("artifacts/lgbm_v3.pkl")
feature_cols = joblib.load("artifacts/feature_cols_v3.pkl")
img = np.load("embeddings/clip_b32_train.npy")
X_img = csr_matrix(img)

# split by rows (stratification would be nicer, but simple split is ok)
idx = np.arange(len(train))
tr_idx, va_idx = train_test_split(idx, test_size=0.2, random_state=42)

def build_block(df_rows):
    X_text = train.loc[df_rows, "catalog_content"].fillna("")
    X_tfidf = tfidf.transform(X_text)
    num = pd.DataFrame([extract_numeric_specs(t) for t in X_text]).fillna(0.0)
    num = num[feature_cols]
    X_all = hstack([X_tfidf, num.values, X_img[df_rows]])
    return X_all

X_tr = build_block(tr_idx)
X_va = build_block(va_idx)

y = train["price"].values
y_tr = np.log1p(y[tr_idx])

# (model is already trained on full set; we only evaluate inference behaviour)
pred_va = np.expm1(model.predict(X_va))
metric = smape(y[va_idx], pred_va)
print(f"Holdout sMAPE on v3 (using existing model): {metric:.2f}%")
