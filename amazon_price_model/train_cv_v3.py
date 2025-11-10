# train_cv_v3.py
import numpy as np
import pandas as pd
import joblib
from pathlib import Path
from sklearn.model_selection import StratifiedKFold
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy.sparse import hstack, csr_matrix
import lightgbm as lgb

from features import extract_numeric_specs

SEED = 42
N_FOLDS = 5
ART = Path("artifacts_cv"); ART.mkdir(exist_ok=True)

def smape(y_true, y_pred):
    denom = (np.abs(y_true) + np.abs(y_pred)) / 2.0
    denom = np.where(denom == 0, 1e-6, denom)
    return np.mean(np.abs(y_pred - y_true) / denom) * 100

def price_bins(y, n_bins=20):
    ylog = np.log1p(y.astype(float))
    edges = np.linspace(ylog.min(), ylog.max(), n_bins + 1)
    return np.digitize(ylog, edges) - 1

print(">> load train")
train = pd.read_csv("data/train.csv")  # sample_id, catalog_content, image_link, price
y = train["price"].astype(float).values
bins = price_bins(train["price"], n_bins=30)

# --- load CLIP embeddings & align by sample_id to be SAFE ---
print(">> load clip train embeddings")
clip_embs = np.load("embeddings/clip_b32_train.npy")         # shape (N,512)
clip_ids  = np.load("embeddings/clip_b32_train_ids.npy")     # shape (N,)
id2row = {int(s): i for i, s in enumerate(clip_ids)}
idx = [id2row[int(sid)] for sid in train["sample_id"].tolist()]
clip_aligned = clip_embs[idx]
X_img_all = csr_matrix(clip_aligned)

# placeholders
oof_pred = np.zeros(len(train), dtype=float)

folds = StratifiedKFold(n_splits=N_FOLDS, shuffle=True, random_state=SEED)

for fold, (tr_idx, va_idx) in enumerate(folds.split(train, bins), 1):
    print(f"\n===== FOLD {fold} =====")
    tr, va = train.iloc[tr_idx], train.iloc[va_idx]
    y_tr = np.log1p(tr["price"].astype(float).values)
    y_va_true = va["price"].astype(float).values

    # text
    tfidf = TfidfVectorizer(max_features=250_000, ngram_range=(1,2), min_df=2)
    Xtr_text = tfidf.fit_transform(tr["catalog_content"].fillna(""))
    Xva_text = tfidf.transform(va["catalog_content"].fillna(""))

    # numeric
    tr_num = pd.DataFrame([extract_numeric_specs(t) for t in tr["catalog_content"].fillna("")]).fillna(0.0)
    va_num = pd.DataFrame([extract_numeric_specs(t) for t in va["catalog_content"].fillna("")]).fillna(0.0)
    feat_cols = tr_num.columns.tolist()
    va_num = va_num[feat_cols]

    # image
    Xtr_img = X_img_all[tr_idx]
    Xva_img = X_img_all[va_idx]

    # fuse
    from scipy.sparse import csr_matrix
    Xtr_all = hstack([Xtr_text, tr_num.values, Xtr_img])
    Xva_all = hstack([Xva_text, va_num.values, Xva_img])

    # model
    params = dict(
        objective="regression",
        metric="rmse",
        learning_rate=0.05,
        num_leaves=200,
        feature_fraction=0.8,
        bagging_fraction=0.8,
        bagging_freq=1,
        seed=SEED,
    )
    dtrain = lgb.Dataset(Xtr_all, label=y_tr)
    model = lgb.train(params, dtrain, num_boost_round=1500)

    # predict on val
    pred_log = model.predict(Xva_all)
    pred = np.expm1(pred_log)
    oof_pred[va_idx] = pred

    # save fold artifacts
    joblib.dump(tfidf, ART / f"tfidf_v3_fold{fold}.pkl")
    joblib.dump(model, ART / f"lgbm_v3_fold{fold}.pkl")
    joblib.dump(feat_cols, ART / f"feature_cols_v3_fold{fold}.pkl")

    fold_smape = smape(y_va_true, pred)
    print(f"[fold {fold}] sMAPE = {fold_smape:.3f}%")

# overall OOF
oof_smape = smape(y, oof_pred)
from sklearn.metrics import mean_squared_error, mean_absolute_error
oof_rmse = mean_squared_error(y, oof_pred, squared=False)
oof_mae = mean_absolute_error(y, oof_pred)
print("\n===== OOF RESULTS (5-fold) =====")
print(f"sMAPE: {oof_smape:.3f}% | RMSE: {oof_rmse:.4f} | MAE: {oof_mae:.4f}")

# dump OOF csv
oof = pd.DataFrame({"sample_id": train["sample_id"], "price_true": y, "price_pred": oof_pred})
oof.to_csv("oof_v3.csv", index=False)
print("saved: oof_v3.csv and artifacts_cv/*")
