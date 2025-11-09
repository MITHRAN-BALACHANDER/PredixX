# generate_image_embeddings_B32.py
import os, io, time, math, hashlib, threading
from queue import Queue
from typing import Tuple, Optional
import numpy as np
import pandas as pd
from PIL import Image, UnidentifiedImageError
import requests
from tqdm import tqdm

import torch
from torchvision import transforms
from transformers import CLIPModel, CLIPProcessor

# ---------- Config ----------
TRAIN_CSV = "data/train.csv"
TEST_CSV  = "data/test.csv"

IMG_DIR   = "image_cache"            # where jpgs get saved
EMB_DIR   = "embeddings"             # where npy outputs go
MODEL_ID  = "openai/clip-vit-base-patch32"  # ViT-B/32
BATCH_SIZE = 64                      # adjust if VRAM < 6GB; CPU ok too
NUM_WORKERS = 16                     # threads for downloading
TIMEOUT = 15                         # seconds per HTTP request
RETRIES = 3
SLEEP_BETWEEN_RETRIES = 1.5
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"

# ---------- Setup ----------
os.makedirs(IMG_DIR, exist_ok=True)
os.makedirs(EMB_DIR, exist_ok=True)

device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using device: {device}")

# ---------- Helpers ----------
def safe_filename(url: str) -> str:
    # stable short hash name to avoid illegal chars
    h = hashlib.blake2b(url.encode("utf-8"), digest_size=16).hexdigest()
    return f"{h}.jpg"

def download_one(url: str, out_path: str) -> bool:
    if os.path.exists(out_path):
        return True
    headers = {"User-Agent": USER_AGENT}
    for _ in range(RETRIES):
        try:
            r = requests.get(url, headers=headers, timeout=TIMEOUT)
            if r.status_code == 200:
                with open(out_path, "wb") as f:
                    f.write(r.content)
                return True
        except requests.RequestException:
            pass
        time.sleep(SLEEP_BETWEEN_RETRIES)
    return False

def pil_open_rgb(path: str) -> Optional[Image.Image]:
    try:
        img = Image.open(path).convert("RGB")
        return img
    except (UnidentifiedImageError, OSError):
        return None

# Threaded downloader
def threaded_download(rows: list, split_tag: str) -> Tuple[list, list]:
    """
    rows: list of (sample_id, image_link)
    returns: (ok_ids, failed_ids)
    """
    q = Queue(maxsize=NUM_WORKERS * 2)
    ok_ids, failed_ids = [], []
    lock = threading.Lock()

    def worker():
        while True:
            item = q.get()
            if item is None:
                break
            sid, url = item
            fname = safe_filename(url)
            out_path = os.path.join(IMG_DIR, fname)
            success = download_one(url, out_path)
            with lock:
                if success:
                    ok_ids.append(sid)
                else:
                    failed_ids.append(sid)
            q.task_done()

    threads = []
    for _ in range(NUM_WORKERS):
        t = threading.Thread(target=worker, daemon=True)
        t.start()
        threads.append(t)

    for sid, url in rows:
        q.put((sid, url))

    q.join()
    for _ in range(NUM_WORKERS):
        q.put(None)
    for t in threads:
        t.join()

    # persist failed list
    if failed_ids:
        with open(os.path.join(EMB_DIR, f"failed_{split_tag}_ids.txt"), "w") as f:
            for x in failed_ids:
                f.write(str(x) + "\n")
    return ok_ids, failed_ids

# ---------- Embedding ----------
@torch.no_grad()
def embed_paths(model, processor, paths: list) -> np.ndarray:
    """
    paths: list of image file paths (len = M)
    returns: (M, 512) float32 CLIP image embeddings (pooled)
    """
    feats = []
    for i in tqdm(range(0, len(paths), BATCH_SIZE), desc="Embedding", ncols=100):
        batch_paths = paths[i:i+BATCH_SIZE]
        images = []
        for p in batch_paths:
            img = pil_open_rgb(p)
            if img is None:
                # create a tiny black image as fallback to keep alignment
                img = Image.new("RGB", (224, 224), color=(0, 0, 0))
            images.append(img)

        inputs = processor(images=images, return_tensors="pt", padding=True)
        inputs = {k: v.to(device) for k, v in inputs.items()}

        out = model.get_image_features(**inputs)  # (B, D)
        # Normalize (CLIP best practice)
        out = out / out.norm(dim=-1, keepdim=True)
        feats.append(out.detach().cpu().float().numpy())
    return np.concatenate(feats, axis=0) if feats else np.zeros((0, 512), dtype=np.float32)

def run_split(df: pd.DataFrame, split_tag: str):
    """
    split_tag: 'train' or 'test'
    Saves:
      embeddings/clip_b32_{split}.npy
      embeddings/clip_b32_{split}_ids.npy
    """
    # 1) download all images (with resume)
    pairs = list(zip(df["sample_id"].tolist(), df["image_link"].tolist()))
    print(f"[{split_tag}] downloading {len(pairs)} images...")
    ok_ids, failed_ids = threaded_download(pairs, split_tag)
    ok_set = set(ok_ids)

    # Create ordered lists aligned to dataframe order
    ordered_ids, ordered_paths = [], []
    for sid, url in pairs:
        fname = safe_filename(url)
        p = os.path.join(IMG_DIR, fname)
        if sid in ok_set and os.path.exists(p):
            ordered_ids.append(sid)
            ordered_paths.append(p)
        else:
            # still append a placeholder so alignment stays with IDs
            ordered_ids.append(sid)
            ordered_paths.append(p)  # path may not exist; embed_paths handles with fallback

    # 2) load CLIP
    print(f"[{split_tag}] loading CLIP model: {MODEL_ID}")
    model = CLIPModel.from_pretrained(MODEL_ID).to(device)
    processor = CLIPProcessor.from_pretrained(MODEL_ID)
    model.eval()

    # 3) embed
    print(f"[{split_tag}] embedding {len(ordered_paths)} images...")
    embs = embed_paths(model, processor, ordered_paths)  # (N, 512)

    # 4) save
    emb_path = os.path.join(EMB_DIR, f"clip_b32_{split_tag}.npy")
    ids_path = os.path.join(EMB_DIR, f"clip_b32_{split_tag}_ids.npy")
    np.save(emb_path, embs)
    np.save(ids_path, np.array(ordered_ids, dtype=np.int64))
    print(f"[{split_tag}] saved: {emb_path}")
    print(f"[{split_tag}] saved: {ids_path}")
    if failed_ids:
        print(f"[{split_tag}] {len(failed_ids)} images failed to download; placeholders embedded.")

def main():
    train = pd.read_csv(TRAIN_CSV, usecols=["sample_id", "image_link"])
    test  = pd.read_csv(TEST_CSV,  usecols=["sample_id", "image_link"])

    # Deduplicate by URL to avoid redundant downloads across splits
    # (but we still emit per-split arrays in original row order)
    print("Starting TRAIN split")
    run_split(train, "train")
    print("Starting TEST split")
    run_split(test, "test")
    print("✅ All done.")

if __name__ == "__main__":
    main()
