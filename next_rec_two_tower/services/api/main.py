import json
from pathlib import Path
from typing import List, Dict

import numpy as np
from fastapi import FastAPI, HTTPException

app = FastAPI(title="Two‑Tower Recommender API", version="0.1.0")

ARTIFACTS = Path(".artifacts")
ITEM_VECS = ARTIFACTS / "item_vecs.npy"
USER_VECS = ARTIFACTS / "user_vecs.npy"
META_JSON = ARTIFACTS / "model_meta.json"
FAISS_INDEX = ARTIFACTS / "faiss_item.index"

try:
    import faiss  # type: ignore
except Exception:
    faiss = None

_index = None
_item_vecs = None
_user_vecs = None
_meta = None


def _load_artifacts():
    global _index, _item_vecs, _user_vecs, _meta
    if META_JSON.exists():
        _meta = json.loads(META_JSON.read_text(encoding="utf-8"))
    if FAISS_INDEX.exists() and faiss is not None:
        _index = faiss.read_index(str(FAISS_INDEX))
    if ITEM_VECS.exists():
        _item_vecs = np.load(ITEM_VECS)
    if USER_VECS.exists():
        _user_vecs = np.load(USER_VECS)


@app.get("/health")
async def health():
    _load_artifacts()
    return {
        "status": "ok",
        "index_loaded": _index is not None,
        "items_vecs": bool(_item_vecs is not None),
        "users_vecs": bool(_user_vecs is not None),
    }


def _ann_search_from_user(user_id: int, k: int = 5) -> List[int]:
    if _user_vecs is None or _item_vecs is None:
        raise HTTPException(status_code=503, detail="Embeddings no disponibles. Entrena primero.")
    if user_id >= _user_vecs.shape[0]:
        raise HTTPException(status_code=404, detail="Usuario fuera de rango.")

    u = _user_vecs[user_id:user_id + 1].astype(np.float32)
    # normalizar para similitud coseno
    u /= (np.linalg.norm(u, axis=1, keepdims=True) + 1e-8)

    if _index is not None:
        D, I = _index.search(u, k)
        return I[0].tolist()
    # Fallback brute-force si FAISS no está
    norms = np.linalg.norm(_item_vecs, axis=1, keepdims=True) + 1e-8
    iv = (_item_vecs / norms).astype(np.float32)
    sims = (iv @ u.T).ravel()
    topk = np.argsort(-sims)[:k]
    return topk.tolist()


@app.get("/rec/{user_id}")
async def recommend(user_id: int, k: int = 5) -> Dict:
    _load_artifacts()
    indices = _ann_search_from_user(user_id, k)
    return {
        "user_id": user_id,
        "k": k,
        "item_indices": indices,
        "note": "Indices corresponden a posicion en item_vecs; mapea a producto_id segun tu catalogo.",
    }
