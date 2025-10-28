import argparse
import os
import json
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Tuple

import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader

# Minimal placeholder Lightning-free training to keep it runnable anywhere
# (You can upgrade to PyTorch Lightning Trainer later.)

class InteractionsDataset(Dataset):
    def __init__(self, interactions: pd.DataFrame, n_users: int, n_items: int):
        self.df = interactions
        self.n_users = n_users
        self.n_items = n_items

    def __len__(self):
        return len(self.df)

    def __getitem__(self, idx):
        row = self.df.iloc[idx]
        return int(row["user_id"]), int(row["producto_id"]), float(row.get("puntuacion", 1.0))

class TwoTower(nn.Module):
    def __init__(self, n_users: int, n_items: int, dim: int = 32):
        super().__init__()
        self.user_emb = nn.Embedding(n_users + 1, dim)
        self.item_emb = nn.Embedding(n_items + 1, dim)

    def forward(self, user_ids, item_ids):
        u = self.user_emb(user_ids)
        i = self.item_emb(item_ids)
        # Dot product similarity
        return (u * i).sum(dim=-1)

    def user_vectors(self):
        return self.user_emb.weight.detach().cpu().numpy()

    def item_vectors(self):
        return self.item_emb.weight.detach().cpu().numpy()


def load_data(data_root: Path) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    users = pd.read_csv(data_root / "usuarios.csv")
    items = pd.read_csv(data_root / "productos.csv")
    inter = pd.read_csv(data_root / "interacciones.csv")
    # Asegurar nombres
    inter = inter.rename(columns={"usuario_id": "user_id", "producto_id": "producto_id", "rating": "puntuacion"})
    # Normalizar ids a consecutivos
    users = users.copy()
    users["user_id"] = users["user_id"].astype(int)
    items = items.copy()
    items["producto_id"] = items["producto_id"].astype(int)
    inter["user_id"] = inter["user_id"].astype(int)
    inter["producto_id"] = inter["producto_id"].astype(int)
    return users, items, inter


def train_baseline(users: pd.DataFrame, items: pd.DataFrame, inter: pd.DataFrame, dim: int = 32, epochs: int = 1, lr: float = 1e-2):
    n_users = int(users["user_id"].max()) + 1
    n_items = int(items["producto_id"].max()) + 1

    model = TwoTower(n_users=n_users, n_items=n_items, dim=dim)
    opt = torch.optim.Adam(model.parameters(), lr=lr)
    ds = InteractionsDataset(inter, n_users, n_items)
    dl = DataLoader(ds, batch_size=512, shuffle=True)

    model.train()
    for ep in range(epochs):
        total = 0.0
        for u, i, y in dl:
            u = u.long()
            i = i.long()
            y = y.float()
            pred = model(u, i)
            loss = ((pred - y)**2).mean()
            opt.zero_grad(); loss.backward(); opt.step()
            total += loss.item() * len(u)
        print(f"epoch={ep+1} loss={total/len(ds):.4f}")
    return model


def build_faiss_index(item_vecs: np.ndarray, artifacts: Path):
    try:
        import faiss  # type: ignore
    except Exception as e:
        print("FAISS no disponible, se omitirá el índice.", e)
        return None
    d = item_vecs.shape[1]
    index = faiss.IndexFlatIP(d)  # inner product
    # normalizar para usar IP como coseno
    norms = np.linalg.norm(item_vecs, axis=1, keepdims=True) + 1e-8
    normed = item_vecs / norms
    index.add(normed.astype(np.float32))
    faiss.write_index(index, str(artifacts / "faiss_item.index"))
    np.save(artifacts / "item_vecs.npy", item_vecs)
    return str(artifacts / "faiss_item.index")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-root", type=str, default=".")
    parser.add_argument("--artifacts", type=str, default=".artifacts")
    parser.add_argument("--epochs", type=int, default=1)
    parser.add_argument("--dim", type=int, default=32)
    args = parser.parse_args()

    data_root = Path(args.data_root)
    artifacts = Path(args.artifacts)
    artifacts.mkdir(parents=True, exist_ok=True)

    users, items, inter = load_data(data_root)
    model = train_baseline(users, items, inter, dim=args.dim, epochs=args.epochs)

    # Export embeddings
    user_vecs = model.user_vectors()
    item_vecs = model.item_vectors()
    np.save(artifacts / "user_vecs.npy", user_vecs)
    np.save(artifacts / "item_vecs.npy", item_vecs)

    index_path = build_faiss_index(item_vecs, artifacts)

    meta = {
        "dim": args.dim,
        "n_users": int(users["user_id"].max()) + 1,
        "n_items": int(items["producto_id"].max()) + 1,
        "index_path": index_path,
    }
    with open(artifacts / "model_meta.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)
    print("Artefactos guardados en", artifacts)

if __name__ == "__main__":
    main()
